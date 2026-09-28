# API Documentation

The RESTful API is documented via FastAPI's native OpenAPI schema. Access it live at `/docs`.

## Key Endpoints
- `GET /api/dashboard/stats`: Top-level application metrics.
- `GET /api/dashboard/analytics`: Returns formatted arrays for Recharts visualizations mapping ENSO frequencies and claims logic.
- `POST /api/data/validate-csv`: Memory-bound DataFrame validation.
- `POST /api/ml/train`: Initiates the model pipeline, registers C-Index, and tags active `ModelVersion`.
- `POST /api/ml/predict`: Runs real-time inference on the active Cox PH Joblib artifact.
- `GET /api/ml/kaplan-meier`: Generates segmented probability arrays for the UI curves.
