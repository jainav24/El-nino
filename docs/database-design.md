# Database Design

The database is strictly normalized to the Third Normal Form (3NF).

1. **Users**: Authentication and RBAC.
2. **Farmers**: Demographics and static agricultural data.
3. **InsurancePolicies**: Coverage details tied to Farmers.
4. **InsuranceClaims**: Event tracking tied to Policies.
5. **WeatherRecords / EnsoRecords**: Time-series climatological data.
6. **SurvivalDataset**: A flattened, materialized table engineered specifically for ML ingestion.
