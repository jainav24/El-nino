# AgriRisk AI - Agricultural Insurance Risk Assessment

![AgriRisk AI](https://img.shields.io/badge/AgriRisk-AI-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-19-blue)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-blue)

AgriRisk AI is a full-stack intelligent platform designed to dynamically evaluate agricultural insurance portfolios against systemic climate risks. By integrating real-time weather anomalies and the Oceanic Niño Index (ENSO data), the platform shifts agricultural underwriting from static historical averages to time-to-event climatological forecasting.

## 🚀 Key Features

* **Machine Learning Risk Engine:** Utilizes Survival Analysis (Kaplan-Meier baseline & Cox Proportional Hazards model) to estimate the probability and timing of insurance claims based on climate variables.
* **Interactive Dashboard:** Offers comprehensive visualizations for data analytics, model insights, and weather patterns using Recharts and Tailwind CSS.
* **What-If Analysis:** Compare different scenarios (e.g., El Niño vs. La Niña) to see how agricultural risk profiles adapt.
* **Real-time AI Assistant:** Integrates with Google Generative AI (Gemini) to interpret complex model outputs and hazard ratios in plain English.
* **End-to-End Pipeline:** Seamlessly trigger dataset ingestion, feature engineering, and ML model retraining directly from the UI.

## 🏗 System Architecture

* **Frontend:** React 19 (TypeScript, Vite), Tailwind CSS v4, Recharts, Framer Motion, React Router.
* **Backend:** FastAPI, Python, SQLAlchemy, Uvicorn.
* **Machine Learning:** Pandas, NumPy, Scikit-Learn, Lifelines (CoxPH).
* **Database:** PostgreSQL (Production) / SQLite (Development), managed via Alembic.
* **AI Integration:** Google Generative AI (Gemini API) for context-aware chat.

## 📁 Project Structure

```text
.
├── backend/            # FastAPI application
│   ├── api/            # API endpoints (routes, auth, chat, ml)
│   ├── core/           # Core configurations
│   ├── data/           # Data processing and seed data
│   ├── database/       # SQLAlchemy models and connection
│   ├── schemas/        # Pydantic validation schemas
│   ├── services/       # Business logic and ML inference wrappers
│   └── main.py         # Application entry point
├── frontend/           # React frontend
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Application pages (Dashboard, Risk, Analysis, etc.)
│   │   ├── services/   # API client services
│   │   └── App.tsx     # Main routing component
│   └── package.json    # Frontend dependencies
├── ml/                 # Machine learning pipeline
│   ├── feature_engineering.py
│   ├── preprocessing.py
│   ├── survival_dataset.py
│   ├── prediction/     # Inference engine
│   └── training/       # Model training logic
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile          # Backend Dockerfile
└── requirements.txt    # Python dependencies
```

## 🛠 Installation & Setup

### Prerequisites
* Python 3.11+
* Node.js 18+
* Docker & Docker Compose (Optional, for containerized deployment)

### 1. Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key
   ```
4. Run the database migrations (if using SQLite, Alembic will initialize it):
   ```bash
   alembic upgrade head
   ```
5. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```

### 2. Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the application at `http://localhost:5173`.

### 3. Docker Deployment

To spin up the entire stack (PostgreSQL + FastAPI backend) using Docker Compose:

```bash
docker-compose up --build
```

*Note: You will still need to run the frontend separately or configure it to be served statically by FastAPI/Nginx.*

## 📈 Methodology: Survival Analysis

The application models agricultural risk using a dual-pronged approach:

1. **Non-Parametric Estimation (Kaplan-Meier):** Calculates baseline survival probabilities across distinct groups to observe macroscopic differences without covariate interference.
2. **Semi-Parametric Modeling (Cox Proportional Hazards):** Fits a penalized maximum likelihood model using interaction terms between ENSO phases, rainfall anomalies, and agricultural traits to extract actionable relative hazard ratios. Dynamic zero-variance filtering is employed to prevent perfect collinearity.

## 🤝 Future Scope

* Implementation of Random Survival Forests (RSF) for capturing complex non-linear feature interactions.
* Direct integration with satellite imagery APIs for plot-level crop health monitoring.

---
*Disclaimer: This platform provides model-based analytical estimates. Predictions should not be interpreted as guaranteed insurance claim outcomes.*
