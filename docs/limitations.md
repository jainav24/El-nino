# Limitations & Future Scope

## Known Limitations
1. **Model Paradigm Constraints**: The Cox PH model inherently enforces a linear relationship between log hazards and covariates. Non-linear relationships might be under-represented.
2. **Geospatial Resolution**: The platform utilizes macro-level regional blocks rather than pixel-perfect geocoordinates, missing micro-climate variability.
3. **External Confounders**: Socio-economic factors and systemic pesticide resistance are not currently logged in the dataset.

## Future Scope
1. **Deep Learning Paradigms**: Exploring DeepSurv (Neural Networks for Survival Analysis) to capture non-linear hazard relationships.
2. **Satellite NDVI Integration**: Connecting direct vegetative satellite feeds into the temporal ingestion loop.
3. **Dynamic Premium Modeling**: Coupling the Cox Hazard Ratios directly into automated financial actuarial models.
