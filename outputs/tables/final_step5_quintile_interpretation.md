# Quintile Analysis Interpretation — Flow-Performance, Active EDC Funds

## 1. Average Flows by Quintile (Unconditional)

| Quintile | Mean Monthly Flow | Mean Flow (pp) |
|---|---|---|
| Q1 (worst) | -0.0135 | -1.352 pp |
| Q2 | -0.0057 | -0.570 pp |
| Q3 | -0.0009 | -0.086 pp |
| Q4 | +0.0057 | +0.569 pp |
| Q5 (best) | +0.0187 | +1.867 pp |
| **Q5 − Q1 spread** | **+0.0322** | **+3.219 pp/month** |

The raw Q5 − Q1 flow spread is **+3.219 pp/month** (+38.62 pp/year annualised).

## 2. Regression-Adjusted Quintile Effects (Model 3: Month FE)

| Quintile | Coef vs Q1 | SE | t | p | Δflow (pp/month) |
|---|---|---|---|---|---|
| Q1 (ref.) | 0.0000 | — | — | — | 0.000 |
| Q2 | +0.0077*** | 0.0007 | 10.99 | 0.0000 | +0.765 pp |
| Q3 | +0.0122*** | 0.0007 | 16.86 | 0.0000 | +1.225 pp |
| Q4 | +0.0189*** | 0.0008 | 22.82 | 0.0000 | +1.893 pp |
| Q5 | +0.0323*** | 0.0012 | 26.63 | 0.0000 | +3.225 pp |

The regression-adjusted Q5 premium over Q1 is **+3.225 pp/month**
(≈ 0.68 SDs of the flow distribution).

## 3. Monotonicity

Coefficients increase monotonically from Q2 to Q5 in:
- (1) Baseline: ✅ monotone
- (2) Controls: ✅ monotone
- (3) Month FE: ✅ monotone
- (4) Month+EDC FE: ✅ monotone

## 4. Convexity / Nonlinearity

Q4→Q5 step size vs. average Q1→Q4 step:
- Q4→Q5 step (Model 3)       : +0.0133 (+1.333 pp)
- Avg Q1→Q4 step per bin     : +0.0063 (+0.631 pp)
- Ratio                      : 2.11x

A ratio >1 indicates a **convex (disproportionate) flow response** at the top — top performers receive more than proportionally higher inflows. This is consistent with the asymmetric flow-performance relationship documented in the literature (e.g., Sirri & Tufano 1998; Chevalier & Ellison 1997).

## 5. Thesis-Readiness

- ✅ DV is flow_winsorized.
- ✅ Q1 is the reference group (not included as regressor).
- ✅ Quintiles assigned for all obs with non-null DV + IV.
- ✅ Q5 is positive and significant in Model 3 (coef=0.0323, p=0.0000).
- ✅ Coefficients Q2–Q5 are monotonically increasing in Model 3.
- ✅ Q5 step (0.0133) is disproportionately larger than avg Q1–Q4 step (0.0063) → convex/nonlinear pattern.

## 6. Summary

- Funds in the top performance quintile (Q5) receive **+3.225 pp/month** more
  flow than bottom-quintile funds (Q1) after controlling for fund characteristics and
  month fixed effects.
- The flow-performance relationship is monotonically increasing across quintiles in the
  preferred specification (Model 3).
- The Q4→Q5 step is disproportionately large, consistent with a convex/nonlinear flow-performance relationship.
- Results are robust to controls and fixed effects across all four model specifications.
