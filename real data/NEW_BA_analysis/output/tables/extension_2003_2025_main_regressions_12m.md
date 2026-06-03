# Flow-Performance Regressions — Extension Sample (2003–2025)

## Table: OLS Regressions — Dependent Variable: Flow (winsorized)

| Variable | (1) Baseline | (2) Controls | (3) Month FE | (4) Month+EDC FE |
| --- | --- | --- | --- | --- |
| Past 12m Return | 0.0219*** | 0.0216*** | 0.1171*** | 0.1173*** |
|  | (0.0011) | (0.0011) | (0.0043) | (0.0043) |
| log(TNA_{t-1}) | — | 0.0000 | -0.0001 | -0.0002 |
|  |  | (0.0002) | (0.0002) | (0.0002) |
| Expense Ratio | — | -0.3297*** | -0.3787*** | -0.3293*** |
|  |  | (0.0754) | (0.0833) | (0.0827) |
| Fund Age (years) | — | -0.0004*** | -0.0003*** | -0.0003*** |
|  |  | (0.0000) | (0.0000) | (0.0000) |
| Turnover Ratio | — | -0.0013*** | -0.0014*** | -0.0016*** |
|  |  | (0.0005) | (0.0005) | (0.0005) |
| Constant | -0.0061*** | 0.0057*** | -0.0405*** | -0.0406*** |
|  | (0.0003) | (0.0018) | (0.0035) | (0.0035) |
| N | 135,585 | 135,585 | 135,585 | 135,585 |
| R² | 0.0115 | 0.0229 | 0.0752 | 0.0759 |
| Adj. R² | 0.0115 | 0.0229 | 0.0734 | 0.0741 |
| Month FE | No | No | Yes | Yes |
| EDC Style FE | No | No | No | Yes |

**Notes:**
Standard errors clustered by WFICN. \*** p<0.01, \** p<0.05, \* p<0.10
Sample: active domestic equity (EDC) funds, 2004–2025 (effective 12m window).
Past 12m Return is the gap-aware cumulative 12-month lagged return (excludes current month; shift(1) + rolling(12) in log-space).
N=135,585 in the full model (missing exp_ratio/turn_ratio reduces N from 170,616 to 135,585).
