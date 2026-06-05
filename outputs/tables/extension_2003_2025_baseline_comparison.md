# Baseline vs. Extension Comparison — Flow-Performance Analysis

| Metric | Baseline (1991–2011) | Extension (2003–2025) |
| --- | --- | --- |
| Sample label | Baseline replication | Extension (own contribution) |
| Raw CRSP period | 1991–2011 | 2003–2025 |
| Effective 12m reg. period | 1999–2011 | 2004–2025 |
| Fund universe | Active EDC (WFICN) | Active EDC (WFICN) |
| Regression N (M3/M4) | 77,140 | 135,585 |
| Unique WFICNs / clusters | 1,215 | 1,120 |
| M3 coef (SE) | 0.0928 (0.0047) | 0.1171 (0.0043) |
| +10 pp past return → flow (M3) | +0.928 pp/month | +1.171 pp/month |
| Flow SD | 5.22 pp | 4.08 pp |
| past_12m_return SD | 24.5 pp | 19.1 pp |
| Q5−Q1 (unconditional means) | +3.22 pp/month | +2.23 pp/month |
| Q5 premium, reg-adj (M3) | +3.230 pp/month | +2.610 pp/month |
| Convexity ratio (M3) | ~2.4× | 3.10× |
| Monotonic Q2→Q5 (M3) | Yes (all 4 models) | Yes (all 4 models) |
| Median lag TNA ($M) | 212 | 306 |
| Median fund age (years) | 8.9 | 14.8 |
| SE clustering | WFICN | WFICN |
| Controls | log_TNA, exp_ratio, age, turnover | log_TNA, exp_ratio, age, turnover |
| FE (M3/M4) | Month / Month+EDC | Month / Month+EDC |

**Notes:** Preferred specification is Model 3 (month FE + controls). Standard errors clustered by WFICN throughout. \*\*\* p<0.01 in all reported coefficients. Convexity ratio = Q4→Q5 step / avg(Q2→Q3 step, Q3→Q4 step). Baseline: active domestic equity (EDC) funds from CRSP 1991–2011. Extension: active EDC funds from CRSP 2003–2025 (own-contribution analysis).
