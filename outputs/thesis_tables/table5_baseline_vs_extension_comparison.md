**Table 5. Baseline vs. Extension Comparison**

| Dimension | Baseline (1991–2011) | Extension (2003–2025) |
|-----------|---------------------|----------------------|
| Raw CRSP period | 1991–2011 | 2003–2025 |
| Effective 12m regression period | 1999–2011 | 2004–2025 |
| Fund universe | Active domestic equity (EDC) | Active domestic equity (EDC) |
| Regression N (M3/M4) | 77,140 | 135,585 |
| Unique WFICNs (clusters) | 1,215 | 1,120 |
| **M3 coefficient (SE)** | **0.0928 (0.0047)** | **0.1171 (0.0043)** |
| +10 pp past return → flow (M3) | +0.928 pp/month | +1.171 pp/month |
| Flow standard deviation | 5.22 pp | 4.08 pp |
| Past 12m return SD | 24.5 pp | 19.1 pp |
| Q5 − Q1 (unconditional means) | +3.22 pp/month | +2.23 pp/month |
| Q5 premium, regression-adjusted (M3) | +3.230 pp/month | +2.610 pp/month |
| Convexity ratio (M3) | ~2.4× | 3.10× |
| Monotonic Q2→Q5 (M3) | Yes — all 4 models | Yes — all 4 models |
| Median portfolio TNA ($M) | 212 | 306 |
| Median fund age (years) | 8.9 | 14.8 |
| SE clustering | WFICN | WFICN |
| Controls | log TNA, exp. ratio, age, turnover | log TNA, exp. ratio, age, turnover |
| Fixed effects (M3 / M4) | Month / Month + EDC | Month / Month + EDC |

*Notes:* Both samples use identical methodology: WFICN-level TNA-weighted return aggregation,
flow = TNA_t/TNA_{t-1} − (1 + R_t) with 28–35 day gap check, 1/99 winsorisation, 12-month
gap-aware rolling past return, OLS with WFICN-clustered standard errors. M3 is the preferred
specification: controls + month fixed effects. Convexity = (Q4→Q5 step) / avg(Q2→Q3 step,
Q3→Q4 step). The extension covers a materially different market environment including the
Global Financial Crisis (2008–2009), the COVID-19 shock (2020), and the 2022 rate cycle.
