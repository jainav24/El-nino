# AgriRisk AI - Current State Audit

## Overview
This document outlines the current state of the "AgriRisk AI" platform before starting Project 31 — Part 1.

## 1. Database
- **Schema & Models:** The SQLAlchemy database schema is fully defined in `backend/database/models.py`.
- **Existing Tables:**
  - `Farmer`
  - `InsurancePolicy`
  - `InsuranceClaim`
  - `WeatherRecord`
  - `EnsoRecord`
  - `SurvivalDataset`
  - `ModelVersion`
  - `PredictionHistory`
  - `User`
- **What is Incomplete:** 
  - The `seed_demo_data` function generates dummy data for Farmers, Policies, Claims, and SurvivalDataset, but **does not generate Weather and ENSO records**.

## 2. API Routes
- **What Works:**
  - `GET /api/dashboard/stats`: Returns basic counts (Farmers, Policies, Claims, Claim Rate).
  - `GET /api/dashboard/analytics`: Returns basic ENSO and Claim risk metrics.
  - Core CRUD routes in `core_routes.py`:
    - `POST /api/farmers`, `GET /api/farmers`
    - `POST /api/policies`, `GET /api/policies`
    - `POST /api/claims`, `GET /api/claims`
  - AI Assistant API in `chat.py`.
  - Machine learning endpoints in `routes.py` and `ml_routes.py`.
- **What is Mocked/Incomplete:**
  - `POST /api/data/store-csv` is completely mocked. It returns a success message but does not insert data into the database.
  - Missing API routes: `GET /api/weather` and `GET /api/enso` do not exist.
  - Missing ID-specific endpoints (e.g., `GET /api/farmers/{id}`).

## 3. Frontend & React Components
- **What Works:**
  - Dashboard layout and navigation structure.
  - Dashboard analytics page (mostly working but depends on real API data).
  - Risk Assessment, Model Insights, Survival Analysis.
  - The Floating AI assistant works perfectly.
- **What is Mocked/Placeholder:**
  - `Farmers` page: `<div>Farmers Page</div>` placeholder.
  - `Policies` page: `<div>Policies Page</div>` placeholder.
  - `Claims` page: `<div>Claims Page</div>` placeholder.
  - `Weather & ENSO` page: `<div>Weather & ENSO Page</div>` placeholder.
  - The Data Upload component only simulates uploads and doesn't actually populate real database entries due to the mocked backend.
- **What Needs Implementation:**
  - Full data tables for Farmers, Policies, and Claims (with filters, pagination, search).
  - Detailed modal/view pages for individual records.
  - A comprehensive "Weather & ENSO" analytics page.
  - Integration of actual backend API responses on the main Dashboard to replace hardcoded values.
