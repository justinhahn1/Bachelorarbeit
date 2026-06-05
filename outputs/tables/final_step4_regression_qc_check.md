# Regression QC Check — Step 4 Main Flow-Performance Regressions

## 1. Dependent Variable

- **Column used:** `flow_winsorized` ✓
- Flow winsorized at 1st/99th percentile; raw flow NOT used as DV.
- `flow_winsorized` range in regression sample: [-0.1779, 0.2897]
- Mean: 0.001537 | Std: 0.047153

## 2. Main Explanatory Variable: past_12m_return

- **Column used:** `past_12m_return` ✓
- Constructed via gap-aware rolling: `shift(1)` before 12-month rolling sum in log-space → current month is excluded.
- Correlation with current-period `portfolio_return_winsorized`: 0.0091 (low → no look-ahead bias).
- Mean: 0.0812 | Std: 0.2440

## 3. Sample Sizes

| Model | N | Unique WFICN | Note |
|---|---|---|---|
| (1) Baseline | 77,140 | 909 | same sample |
| (2) Controls | 77,140 | 909 | same sample |
| (3) Month FE | 77,140 | 909 | same sample |
| (4) Month+EDC FE | 77,140 | 909 | same sample |

All four models use the same 77,140-observation sample, formed by listwise deletion of
all required variables before any model is estimated. N is identical across models.

**Sample attrition from full dataset:**

| Step | N | Change |
|---|---|---|
| Full loaded dataset | 99,325 | — |
| After dropping NaN in flow_winsorized + past_12m_return + log_lag_tna + exp_ratio + fund_age_years | 77,309 | |
| After also requiring turn_ratio non-null | 77,140 | −169 (0.2%) |

**turn_ratio note:** turn_ratio removes 169 observations (0.2% of the no-turn-ratio sample).
This is modest (<10%) and does not distort the main results.

## 4. Controls

Controls included in Models 2–4: `log_lag_tna`, `exp_ratio`, `fund_age_years`, `turn_ratio`.

| Variable | Mean | Std | Min | Max |
|---|---|---|---|---|
| log_lag_tna | 5.5609 | 1.4701 | 2.3026 | 10.6423 |
| exp_ratio | 0.0133 | 0.0039 | 0.0000 | 0.0889 |
| fund_age_years | 11.6148 | 8.6158 | 1.2485 | 74.2204 |
| turn_ratio | 0.9708 | 0.8287 | 0.0000 | 21.9600 |

## 5. Fixed Effects

| Feature | Model 2 | Model 3 | Model 4 |
|---|---|---|---|
| Month dummies | No | Yes | Yes |
| EDC style dummies | No | No | Yes |

- **Month FE:** 141 unique months → 140 dummies (drop_first=True). Baseline month: 2000-04.
- **EDC style FE:** 3 categories (['EDCI', 'EDCM', 'EDCS']) → 2 dummies (EDCS = baseline). Dummies: ['edc_EDCI', 'edc_EDCM'].

## 6. Standard Errors

All four models use **WFICN-clustered standard errors** (`cov_type='cluster'`, `groups=wficn`).
Unique clusters: 909 WFICNs.

## 7. Coefficient Plausibility: past_12m_return

| Model | Coef | SE | t-stat | p-value | Sig | N | R² |
|---|---|---|---|---|---|---|---|
| (1) Baseline | +0.0209 | 0.0013 | 15.81 | 0.0000 | *** | 77,140 | 0.0117 |
| (2) Controls | +0.0201 | 0.0013 | 15.11 | 0.0000 | *** | 77,140 | 0.0229 |
| (3) Month FE | +0.0928 | 0.0047 | 19.85 | 0.0000 | *** | 77,140 | 0.0867 |
| (4) Month+EDC FE | +0.0943 | 0.0046 | 20.63 | 0.0000 | *** | 77,140 | 0.0891 |

### Economic Effect of +10 pp in past_12m_return

| Model | Δflow (pp) | As % of SD(flow) |
|---|---|---|
| (1) Baseline | +0.209 pp | 4.4% |
| (2) Controls | +0.201 pp | 4.3% |
| (3) Month FE | +0.928 pp | 19.7% |
| (4) Month+EDC FE | +0.943 pp | 20.0% |

SD of `flow_winsorized` = 4.72 pp.

### Interpretation of Model 2 → Model 3 Jump (0.0201 → 0.0928, ratio 4.61×)

Without month fixed effects (Models 1–2), the regression pools both cross-sectional
(fund vs. fund in the same month) and time-series (boom vs. bust years) variation.
Time-series co-movement between market-level past returns and aggregate flows dilutes
the true within-period performance-chasing coefficient: in aggregate, flows respond
weakly to past market-level returns compared to how strongly fund-level flows respond
to relative performance within a period.

Adding month dummies (Model 3) absorbs all period-specific shocks and isolates the
cross-sectional relationship: *conditional on knowing the market environment, do
relatively better-performing funds receive relatively more inflows?* The answer is
a stronger yes than the pooled estimate implied. This pattern is standard in the
mutual fund literature and is **not a red flag**. The sign, significance, and
direction are unchanged; only the magnitude rises.

## 8. Verdict

- ✅ DV is flow_winsorized (correctly winsorized).
- ✅ past_12m_return shows low corr with current return (0.009) — lag is plausible.
- ✅ All 4 models use the same N = 77,140 (consistent sample).
- ✅ turn_ratio cost is modest (0.2%).
- ✅ FE structure correct: month in M3/M4, EDC only in M4.
- ✅ All models use WFICN-clustered SEs.
- ✅ past_12m_return is positive and p<0.01 in all 4 models.

**THESIS-READY. All specification checks pass.**
