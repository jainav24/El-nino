# 🌾 AgriRisk AI — Revised Problem Statement & Project Brief

> **Target Ecosystem**: Pradhan Mantri Fasal Bima Yojana (PMFBY), Empaneled Agricultural Insurers, State Agriculture Departments, & Rural Lending Banks.

---

## 📌 Executive Summary & Viva Pitch (30-Second Summary)

Our platform is not a direct-to-consumer insurance store selling policies to impoverished farmers. It is a **B2B / B2G Risk Intelligence & Actuarial Engine** built for **PMFBY-empaneled insurance companies and government administrators**, paired with a **free, public early-warning advisory portal for farmers**.

Under PMFBY, the central and state governments already subsidize 95% to 98% of crop insurance premiums. The actual crisis is **systemic under-reserving and catastrophic claim settlement delays during El Niño cycles**, where insurers face sudden claim surges and take 6 to 12 months to verify and disburse payments. By modeling both the **probability and exact timing (time-to-event)** of crop failure under ENSO anomalies using Survival Analysis (Cox Proportional Hazards), our platform enables insurers to reserve capital accurately, settle claims rapidly, and provide farmers with proactive, free advisories to prevent crop loss before it occurs.

---

## 🔄 Paradigm Shift: Old Framing vs. Revised Framing

| Dimension | Old Problem Statement ❌ | Revised Problem Statement ✅ |
|---|---|---|
| **Target User** | Individual smallholder farmers | PMFBY Insurers (AIC, ICICI Lombard, Bajaj Allianz, etc.), State Agriculture Departments, & KCC Lending Banks |
| **Who Pays?** | Farmer (unrealistic for smallholders in distress) | Institutional underwriters & government bodies (farmers pay only a nominal 1.5–2% under PMFBY; government subsidizes 95–98%) |
| **Core Problem** | "Farmers don't have access to insurance" | "Insurers rely on static 5-year averages, leading to massive claim delays and insolvency during El Niño droughts" |
| **Model Formulation** | Binary classification (*Claim vs. No Claim*) | Survival Analysis (*When will the claim occur, and how does El Niño amplify the continuous hazard rate?*) |
| **Farmer's Direct Benefit** | Assumes farmer buys private policy | **1.** Rapid claim settlement when crops fail.<br>**2.** Free, public Farmer Advisory Portal with crop & drought advisories 30–60 days in advance. |

---

## 📝 Formal Revised Problem Statement

### 1. Title
**AI-Driven Risk Intelligence & Survival Analysis for PMFBY Crop Insurance Portfolios under El Niño Weather Anomalies**

### 2. Context & Background
Under India's **Pradhan Mantri Fasal Bima Yojana (PMFBY)**, over 5.5 crore farmers are insured annually, with the central and state governments subsidizing 95% to 98% of the actuarial premium. Farmers pay only a nominal token premium (2% for Kharif crops, 1.5% for Rabi crops, and 5% for commercial/horticultural crops).

However, the operational sustainability of the scheme is repeatedly destabilized during **El Niño-Southern Oscillation (ENSO)** climate anomalies. 

### 3. The Core Problem Breakdown
1. **Actuarial Blind Spots to Climatological Shocks:**
   Traditional underwriting models rely on backward-looking 5-year historical loss averages and binary classifiers (*Claim vs. No Claim*). They fail to model **time-to-event dynamics** (at what stage of the crop growth cycle failure occurs) and treat recurring El Niño climate shocks as unpredictable outliers rather than measurable hazard shifts.
2. **Liquidity Shocks & Extreme Claim Delays for Farmers:**
   When an El Niño event causes widespread monsoon deficits, claim ratios surge unexpectedly by 300%–500%. Because insurers fail to anticipate the volume and timing of claims, actuarial reserves are depleted, resulting in protracted audits, disputes, and claim delays lasting **6 to 12 months**. For small and marginal farmers already burdened by input loans, delayed compensation leads to debt traps and catastrophic distress.
3. **Absence of Pre-Season Public Advisory:**
   Underwriting data and climate telemetry remain locked in corporate silos instead of empowering the farming community with proactive guidance on drought-tolerant crop switching, sowing delays, and moisture conservation before the season begins.

### 4. The Proposed Solution
This project presents an **AI-driven Risk Assessment and Survival Analysis Engine** that integrates the **Oceanic Niño Index (ONI)** with district-level weather telemetry. Using **Cox Proportional Hazards** and **Kaplan-Meier survival estimation**, the platform models the survival probability and hazard rate of insured crops continuously over time.

- **For Insurers and Government Bodies**: Stress-test portfolios under simulated El Niño scenarios, price risk dynamically, and pre-allocate liquidity for accelerated claim settlements.
- **For Farmers**: Access a **free, public early-warning advisory portal** that translates complex climate risk models into actionable agronomic guidance at the district level without needing accounts or subscriptions.

---

## 🎯 Revised Objectives (Mapped to Codebase)

| # | Revised Objective | Implementation in Codebase |
|---|---|---|
| **1** | **Survival Risk Modeling:** Build a Cox Proportional Hazards (Cox-PH) and Kaplan-Meier engine to predict claim probability and timing under ENSO phases. | [`backend/ml/`](file:///c:/Users/Admin/elnino/backend/ml) & [`ml/training/`](file:///c:/Users/Admin/elnino/ml/training) |
| **2** | **Climate Anomaly Feature Engineering:** Integrate Oceanic Niño Index (ONI) and district-level rainfall deviations without post-event data leakage. | [`backend/ml/feature_engineering.py`](file:///c:/Users/Admin/elnino/backend/ml/feature_engineering.py) |
| **3** | **Scenario Stress-Testing:** Enable what-if scenario simulations (Neutral vs. Moderate vs. Strong El Niño) to observe portfolio risk and claim timeline shifts. | [`backend/api/routes.py`](file:///c:/Users/Admin/elnino/backend/api/routes.py) (`POST /what-if`) |
| **4** | **Public Farmer Early-Warning Advisory:** Provide a free, no-login advisory interface delivering crop-specific drought mitigation strategies, risk alerts, and PMFBY zone guidance. | [`backend/api/advisory.py`](file:///c:/Users/Admin/elnino/backend/api/advisory.py) & [`frontend/src/pages/FarmerAdvisory.tsx`](file:///c:/Users/Admin/elnino/frontend/src/pages/FarmerAdvisory.tsx) |
| **5** | **AI-Powered Explainability:** Utilize Google Gemini to translate complex log hazard ratios and survival curves into plain-language actuarial reports. | [`backend/api/chat.py`](file:///c:/Users/Admin/elnino/backend/api/chat.py) |

---

## 🛡️ Viva Defense: Answers to Critical Faculty Questions

### Q1: *"Farmers in India have no money and are committing suicide. How can they afford your private insurance platform?"*
> **Answer:**
> *"Our project does not sell private insurance policies to individual farmers. In India, farmers are covered under PMFBY, where the **Central and State governments pay 95% to 98% of the premium**—farmers only contribute a nominal 1.5% to 2%. 
> Our system is an **actuarial underwriting and liquidity-planning tool for PMFBY-empaneled insurance companies and state agriculture departments**. Currently, insurers suffer huge losses and freeze payouts because they cannot model El Niño risks dynamically. Our system solves backend underwriting so government-subsidized claims reach farmers in weeks rather than months."*

### Q2: *"What direct benefit does a smallholder farmer receive from this project?"*
> **Answer:**
> *"Two direct benefits:
> 1. **Liquidity Before Default:** Accurately predicted claim timelines ensure insurers maintain adequate capital reserves before harvest failure, preventing the 6–12 month payout delays that drive indebted farmers to distress.
> 2. **Free Public Advisory Portal:** We developed a public, zero-cost Farmer Advisory module (accessible without login) that provides farmers with 30–60 day advance warnings regarding El Niño impacts on their specific crop and district, recommending drought-resistant seeds (e.g., Sahbhagi Dhan) and altered sowing schedules."*

### Q3: *"Why use Survival Analysis instead of standard classification like Random Forest or XGBoost?"*
> **Answer:**
> *"Binary classification only answers 'Will there be a claim? Yes or No.' In agricultural underwriting, **timing is critical**. A crop failure during the vegetative phase (Day 30) represents a different loss profile and payout structure than a failure at harvest (Day 110). 
> **Survival Analysis (Cox Proportional Hazards)** handles right-censoring (policies that conclude without a claim) and continuously predicts the baseline hazard function across the 120–150 day season as El Niño conditions intensify."*
