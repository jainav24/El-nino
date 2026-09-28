# 5-Minute Final Demonstration Flow

**Project:** AI-Driven Risk Assessment Model for Agricultural Insurance Claims under El Niño Weather Anomalies using Survival Analysis

## Goal
Demonstrate to the examiners that the project is a fully integrated, academically sound system that successfully combines survival analysis (Cox-PH) with climate data to predict agricultural insurance risk without data leakage.

## Preparation (Before Demo)
1. Ensure the Python virtual environment is active: `.\venv\Scripts\activate`
2. Start the FastAPI backend: `uvicorn backend.main:app --reload`
3. Start the React frontend: `cd frontend && npm run dev`
4. Open the frontend in the browser (usually `http://localhost:5173`)

---

## Step 1: Introduction (0:00 - 0:30)
* **Action:** Open the **About** page.
* **Talking Point:** "Welcome to our final year project. Traditional agricultural insurance models predict IF a claim will happen (binary). We built a Survival Analysis engine using the Cox Proportional Hazards model that predicts WHEN a claim will happen, and how specific climate factors—specifically El Niño—accelerate that risk."

## Step 2: The Dashboard & Architecture (0:30 - 1:00)
* **Action:** Navigate to the **Dashboard**.
* **Talking Point:** "Here you can see the system architecture at work. The React frontend communicates with our FastAPI backend. The backend hosts our trained Cox-PH model. We've processed 10,000 synthetic records, rigorously avoiding data leakage by ensuring no post-event variables (like final crop yield or claim count) are exposed to the model during training."

## Step 3: Running a Prediction (1:00 - 2:00)
* **Action:** Click **New Assessment** and navigate to the form.
* **Talking Point:** "Let's assess a hypothetical farm in Maharashtra growing Cotton."
* **Action:** Leave most defaults, but explicitly point out the **Climate & ENSO Integration** section. Set El Niño status to 'Active El Nino' and Intensity to 'Strong El Nino'.
* **Action:** Click **Assess Risk**.
* **Talking Point:** "The FastAPI backend receives this payload, applies our deterministic feature engineering pipeline (including interaction terms like El Niño x Rainfall Deficit), and feeds it to the Cox model."

## Step 4: Explainability & Hazard Ratios (2:00 - 3:00)
* **Action:** Review the **Analysis Result** page.
* **Talking Point:** "The engine predicted a [High/Critical] risk. But more importantly, this is an Explainable AI (XAI) system. Notice the Top Hazard Ratios chart. A ratio above 1.0 multiplies the baseline risk. You can see exactly *why* the model made this prediction—for example, the 'El Niño exacerbated Rainfall Deficit' factor is driving the risk up."
* **Action:** Scroll down to the Survival Probability Curve.
* **Talking Point:** "This curve shows the probability of the farm surviving WITHOUT a claim over 180 days. You can see the steep drop caused by the climate stress."

## Step 5: What-If Analysis (3:00 - 4:00)
* **Action:** Navigate to the **What-If Analysis** tab.
* **Talking Point:** "Insurers need to know how mitigation strategies affect risk. Let's compare our current 'Strong El Niño' scenario with an alternative."
* **Action:** In the Alternative Scenario, change **Irrigation** to 'Drip' and **El Nino Status** to 'Neutral'. Click **Compare Scenarios**.
* **Talking Point:** "The system dynamically computes the delta. As you can see, investing in Drip Irrigation during a Neutral year dramatically decreases the risk score. This proves our interaction features (like Irrigation Vulnerability to Drought) are working mathematically."

## Step 6: Model Validation & Scientific Rigor (4:00 - 4:45)
* **Action:** Navigate to the **Model Insights** tab.
* **Talking Point:** "To prove our hypothesis, we evaluated the model using the Concordance Index (C-Index). A standard baseline model achieved a C-Index of ~0.72. By explicitly adding El Niño and interaction features, our proposed model improved the C-Index to ~0.73. We also validated this out-of-sample with a Brier Score of ~0.17 at 180 days, proving the model is well-calibrated and not overfitted."

## Step 7: Conclusion & Q&A (4:45 - 5:00)
* **Action:** Navigate to **Historical Analytics** to show the database integration (SQLite saving predictions).
* **Talking Point:** "In conclusion, we've built a robust, leak-free, full-stack machine learning application that brings explainable climate risk modeling to agricultural insurance. We are now open for questions."
