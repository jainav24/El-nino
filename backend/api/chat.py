import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import google.generativeai as genai

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    page_context: Optional[Dict[str, Any]] = None
    risk_context: Optional[Dict[str, Any]] = None
    think_mode: bool = False

SYSTEM_PROMPT = """You are an intelligent, helpful AI assistant built into the 'AgriRisk AI' dashboard.
The project is titled 'AI-Driven Risk Assessment Model for Agricultural Insurance Claims under El Niño Weather Anomalies using Survival Analysis'.

Your job is to answer user questions about the project, the data, the charts, and the underlying machine learning models (Survival Analysis, Kaplan-Meier, Cox Proportional Hazards).
Keep your answers short, clear, simple, conversational, and highly useful. Explain concepts in simple language suitable for a college student.
For simple doubts: 2-5 sentences.
For technical questions: Use short bullets when useful.

CRITICAL RULES:
1. Do NOT invent or hallucinate actual numerical predictions or probabilities for specific farmers/policies unless the data is explicitly provided to you in the context. The ML model is responsible for actual numerical predictions. You are just explaining the results or concepts.
2. If the user asks about the page they are currently on, use the provided context to guide your answer.
3. If the user asks why a particular policy is high/low risk, use the provided risk_context. Explain which parameters drove the prediction based on general survival analysis principles.
4. Do NOT show chain-of-thought or hidden reasoning. Just provide the final answer.
"""

from backend.database.connection import get_db
from backend.services.data_service import get_db_stats
from sqlalchemy.orm import Session

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Prepend system context and page context
    db_stats = get_db_stats(db)
    
    context_str = f"DATABASE STATISTICS:\n{db_stats}\n\n"
    context_str += "CURRENT PAGE CONTEXT:\n" + str(req.page_context) if req.page_context else "No specific page context provided."
    if req.risk_context:
        context_str += f"\n\nCURRENT RISK PREDICTION CONTEXT:\n{req.risk_context}"
        
    if req.think_mode:
        context_str += "\n\nUSER REQUESTED THINK MODE: Please provide a slightly more detailed and thorough explanation for the next question."
        
    last_msg = req.messages[-1].content.lower()

    if not api_key:
        # ---------------------------------------------------------
        # Sophisticated Mocked Response (Fallback when no API Key)
        # ---------------------------------------------------------
        import asyncio
        await asyncio.sleep(1.5) # Simulate network delay
        
        response = ""
        
        # Hazard Ratio logic
        if "hazard ratio" in last_msg or "hr" in last_msg:
            response = "**Hazard Ratio (HR)** is a measure from survival analysis (Cox Proportional Hazards model).\n\n"
            response += "- **HR > 1**: The entity is at a higher risk of experiencing the event (filing a claim) compared to the baseline.\n"
            response += "- **HR < 1**: The entity is at a lower risk.\n\n"
            if req.risk_context and req.risk_context.get('result'):
                hr = req.risk_context['result'].get('hazard_ratio', 1.0)
                response += f"In your current context, the predicted Hazard Ratio is **{hr:.2f}x**, meaning they are {hr:.2f} times more likely to file a claim relative to the average baseline policy."
        
        # Survival Probability logic
        elif "survival" in last_msg or "probability" in last_msg:
            response = "Survival Probability refers to the estimated chance that a policy will **survive** (not file a claim) over a specific time period (e.g., 30, 60, or 90 days).\n\n"
            if req.risk_context and req.risk_context.get('result'):
                sp = req.risk_context['result'].get('survival_probabilities', {})
                response += "Based on the current prediction on your screen:\n"
                for time, prob in sp.items():
                    response += f"- **{time.replace('_', ' ').title()}**: {prob * 100:.1f}%\n"
        
        # Page specific context logic
        elif "this page" in last_msg or "what is this" in last_msg or "explain" in last_msg:
            path = req.page_context.get('pathname', '') if req.page_context else ''
            if "risk-assessment" in path:
                response = "You are currently on the **Risk Assessment** page. This tool allows you to select a specific insurance policy from the database, fetch its contextual climate and farmer data, and run it through our trained Cox Proportional Hazards model to generate a **Hazard Ratio** and a **Survival Curve**."
            elif "model-training" in path:
                response = "This is the **Model Training & Versioning** page. Here you can see the total number of records available in your database. When you click 'Train Cox Model', the system joins Policy, Weather, and Claims data into a Survival Dataset and trains a new Cox PH model, saving its C-Index and coefficients."
            elif "dashboard" in path or path == "/":
                response = "This is the main **Overview Dashboard**. It provides high-level metrics on the total number of farmers, active policies, total claims, and the current active El Niño Southern Oscillation (ENSO) phase."
            elif "data-upload" in path:
                response = "You are on the **Data Ingestion** page. This is used by administrators to bulk-upload historical CSV data (Farmers, Policies, Claims, Weather, ENSO). The system validates foreign keys (e.g. Policies must belong to existing Farmers) before inserting them into the database."
            elif "analytics" in path or "survival-analysis" in path:
                response = "This is the **Analytics** section. It provides aggregated views and interactive charts showing how claim occurrences are distributed across regions, crops, and weather anomalies. It also shows aggregated Kaplan-Meier survival curves."
            else:
                response = "I see you are browsing the AgriRisk AI platform! Let me know if you have specific questions about the data or models here."

        # Think Mode logic
        elif req.think_mode:
            response = "*(Think Mode Active)*\n\nTo answer this thoroughly: AgriRisk AI leverages the **Cox Proportional Hazards (Cox PH)** model because traditional logistic regression fails to account for *time-to-event* and *censored data* (policies that ended without a claim).\n\n"
            response += "By incorporating dynamic covariates like **Temperature Anomaly** and **Rainfall Anomaly** joined dynamically via SQL, the model accurately assesses the elevated hazard caused by El Niño.\n\n"
            response += f"Currently, the system has **{db_stats.get('total_policies', 0)} policies** and **{db_stats.get('total_claims', 0)} claims** to learn from."

        else:
            response = "I am the AgriRisk AI assistant. I can explain the models, define statistical terms like 'Hazard Ratio' or 'Concordance Index', or explain the data on your current screen. How can I help you?"

        return {"response": response}

    # ---------------------------------------------------------
    # Actual Gemini Implementation
    # ---------------------------------------------------------
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        model_name='gemini-3.8-flash',
        system_instruction=SYSTEM_PROMPT + "\n\n" + context_str
    )
    
    # Format messages for gemini (user/model)
    history = []
    for msg in req.messages[:-1]: # all but last
        role = "user" if msg.role == "user" else "model"
        history.append({"role": role, "parts": [msg.content]})
        
    try:
        chat = model.start_chat(history=history)
        gemini_response = chat.send_message(last_msg)
        return {"response": gemini_response.text}
    except Exception as e:
        return {"response": f"AI Error (Check API Key or connection): {str(e)}"}

