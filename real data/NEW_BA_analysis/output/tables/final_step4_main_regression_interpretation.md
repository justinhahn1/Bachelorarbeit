# Regression Interpretation — Flow-Performance, Active EDC Funds

## Main Finding

The coefficient on *Past 12m Return* measures the sensitivity of fund flows to
lagged 12-month performance.

| Model | Coef. | SE | p-value | Sig. (5%) |
|---|---|---|---|---|
| (1) Baseline | +0.0209 | 0.0013 | 0.0000 | Yes |
| (2) Controls | +0.0201 | 0.0013 | 0.0000 | Yes |
| (3) Month FE | +0.0928 | 0.0047 | 0.0000 | Yes |
| (4) Month+EDC FE | +0.0943 | 0.0046 | 0.0000 | Yes |

**A positive coefficient** means that funds with higher past returns attract
more inflows (a flow-chasing / performance-chasing pattern), consistent with
the empirical literature (e.g., Sirri & Tufano 1998; Barber et al. 2022).

## Economic Magnitude

- Standard deviation of past_12m_return: **24.40 pp**
- Standard deviation of flow_winsorized: **4.72 pp**

A one-SD increase in past 12-month return is associated with a
**+2.27 pp** change in monthly flow (Model 3, month FE),
equivalent to **0.48 standard deviations** of the flow distribution.

## Controls

- **log(TNA_{t-1})**:  larger funds attract proportionally smaller flows (scale effect).
- **Expense Ratio**: funds with higher fees are expected to receive lower flows.
- **Fund Age**: older funds grow more slowly.
- **Turnover Ratio**: proxy for trading activity / active management intensity.

## Fixed Effects

Month fixed effects (Model 3) absorb all time-series variation in aggregate
flows (market-wide flow cycles), isolating the cross-sectional
performance-flow relationship.  EDC style fixed effects (Model 4) further
control for systematic differences in flows across small-cap, mid-cap, and
institutional mandate sub-categories.

## Sample Notes

- Period: 2000-04-28 to 2011-12-30
- N (full model): 77,140 WFICN-month observations
- Unique funds: 909 WFICNs
- Fund universe: active domestic equity (EDC) funds only
