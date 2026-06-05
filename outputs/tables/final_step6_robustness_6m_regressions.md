# 6-Month Robustness — Continuous Performance Regressions

## Table: OLS Regressions — DV: flow_winsorized, IV: past_6m_return

| Variable | (1) Baseline | (2) Controls | (3) Month FE | (4) Month+EDC FE |
| --- | --- | --- | --- | --- |
| Past 6m Return | 0.0362*** | 0.0358*** | 0.1319*** | 0.1334*** |
|  | (0.0018) | (0.0018) | (0.0058) | (0.0058) |
| log(TNA_{t-1}) | — | 0.0001 | 0.0002 | 0.0001 |
|  |  | (0.0003) | (0.0003) | (0.0003) |
| Expense Ratio | — | -0.1856* | -0.2069* | -0.1176 |
|  |  | (0.1052) | (0.1068) | (0.1079) |
| Fund Age (years) | — | -0.0007*** | -0.0006*** | -0.0006*** |
|  |  | (0.0001) | (0.0001) | (0.0001) |
| Turnover Ratio | — | -0.0008 | -0.0010* | -0.0012* |
|  |  | (0.0006) | (0.0006) | (0.0006) |
| Constant | 0.0013*** | 0.0112*** | -0.0052 | -0.0067** |
|  | (0.0004) | (0.0025) | (0.0033) | (0.0033) |
| N | 83,319 | 83,319 | 83,319 | 83,319 |
| R² | 0.0157 | 0.0288 | 0.0805 | 0.0827 |
| Adj. R² | 0.0157 | 0.0287 | 0.0789 | 0.0810 |
| Month FE | No | No | Yes | Yes |
| EDC FE | No | No | No | Yes |

**Notes:** Standard errors clustered by WFICN. \*\*\* p<0.01, \*\* p<0.05, \* p<0.10. Sample: active EDC funds.
