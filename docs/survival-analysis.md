# Survival Analysis

## The Framework
Survival Analysis evaluates the expected duration of time until one or more events happen (e.g., crop failure/insurance claim).

### Kaplan-Meier Estimator
A non-parametric statistic used to estimate the survival function from lifetime data. We utilize this to visualize categorical splits, most notably observing the diverging survival probabilities between **El Niño** and **La Niña** policies.

### Cox Proportional Hazards Model
The core prediction engine. The model operates on the hazard function:
$h(t|X) = h_0(t) \exp(\beta X)$

- **$h_0(t)$**: The baseline hazard function.
- **$\beta X$**: The covariate vector and associated coefficients.
- **Hazard Ratio**: Extracted via $\exp(\beta)$. A ratio > 1 indicates increased risk.

### Proportional Hazards Assumption
Tested dynamically utilizing Schoenfeld residuals to guarantee the relationship between covariates and risk remains proportionally consistent over the policy lifetime.
