# Utility & Developer Scripts

This directory contains standalone management, testing, and data generation utilities for the AgriRisk AI platform.

## Available Scripts

| Script | Purpose | Command |
|---|---|---|
| `reset_db.py` | Drops all tables and re-initializes schema in SQLite / PostgreSQL. | `python scripts/reset_db.py` |
| `retrain.py` | Triggers background model retraining via the FastAPI `/api/retrain` endpoint. | `python scripts/retrain.py` |
| `manual_api_test.py` | Runs smoke tests against health, model info, prediction, what-if, and advisory APIs. | `python scripts/manual_api_test.py` |
| `generate_synthetic_dataset.py` | Generates 10,000 synthetic farmer/policy records with weather anomalies and EDA plots into `data/`. | `python scripts/generate_synthetic_dataset.py --rows 10000` |

## Sample Payloads

- `samples/sample_request.json`: Test payload for `/api/predict` (farmer crop risk assessment).
- `samples/sample_whatif.json`: Test payload for `/api/what-if` (scenario simulation).
