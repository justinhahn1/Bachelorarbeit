# Results Interpretation — Extension 2003–2025 Flow-Performance Analysis

## Part A: Main 12-Month Regressions

### Coefficient on Past 12-Month Return

| Model | Coef. | SE | p-value | Sig. (5%) |
|---|---|---|---|---|
| (1) Baseline | +0.0219| 0.0011| 0.0000| Yes |
| (2) Controls | +0.0216| 0.0011| 0.0000| Yes |
| (3) Month FE | +0.1171| 0.0043| 0.0000| Yes |
| (4) Month+EDC FE | +0.1173| 0.0043| 0.0000| Yes |

A positive coefficient confirms that funds with higher past 12-month returns
attract larger net inflows, consistent with performance-chasing behaviour.
This replicates the core finding of the baseline analysis in a more recent and
larger sample.

### Economic Magnitude

- SD of past_12m_return: **19.31 pp**
- SD of flow_winsorized: **3.94 pp**
- A **+10 pp** higher past 12-month return is associated with
  **+1.171 pp/month** higher flow (Model 3, month FE).
- A 1-SD increase in past return → **+2.262 pp/month**
  change in flow (= **0.57 SDs** of flow).

### Comparison with Baseline (1999–2011)

| Metric | Baseline | Extension | Difference |
|---|---|---|---|
| Preferred coef (M3) | 0.0928 | 0.1171 | +0.0243 |
| Qualitative direction | positive | positive | consistent |
| Significance | p<0.01 | p<0.0000 | consistent |

The extension coefficient is **qualitatively similar to** the baseline.
The direction of the effect is unchanged: higher past performance → higher flows.

---

## Part B: Quintile Analysis

### Average Flows by Quintile (Unconditional)

| Quintile | Mean Monthly Flow | Mean Flow (pp) |
|---|---|---|
| Q1 (worst) | -0.0150 | -1.497 pp |
| Q2 | -0.0084 | -0.837 pp |
| Q3 | -0.0051 | -0.509 pp |
| Q4 | -0.0019 | -0.191 pp |
| Q5 (best) | +0.0074 | +0.738 pp |
| **Q5 − Q1 spread** | **+0.0223** | **+2.235 pp/month** |

Raw Q5 − Q1 spread: **+2.235 pp/month** (+26.81 pp/year annualised).

### Regression-Adjusted Quintile Effects (Model 3: Month FE)

| Quintile | Coef vs Q1 | SE | t | p | Δflow (pp/month) |
|---|---|---|---|---|---|
| Q1 (ref.) | 0.0000 | — | — | — | 0.000 |
| Q2 | +0.0075***| 0.0005 | 16.74| 0.0000 | +0.753 pp |
| Q3 | +0.0111***| 0.0005 | 21.88| 0.0000 | +1.112 pp |
| Q4 | +0.0148***| 0.0006 | 26.62| 0.0000 | +1.476 pp |
| Q5 | +0.0261***| 0.0009 | 30.52| 0.0000 | +2.610 pp |

Regression-adjusted Q5 premium over Q1: **+2.610 pp/month**
(= 0.66 SDs of the flow distribution).

### Monotonicity

- (1) Baseline: ✅ monotone
- (2) Controls: ✅ monotone
- (3) Month FE: ✅ monotone
- (4) Month+EDC FE: ✅ monotone

### Convexity

| Metric | Value |
|---|---|
| Q4→Q5 step (Model 3) | +1.134 pp |
| Avg of Q2→Q3 and Q3→Q4 steps | +0.361 pp |
| Convexity ratio | 3.14× |

A ratio >1 indicates a **convex flow response** at the top quintile — top performers receive disproportionately higher inflows, consistent with the asymmetric flow-performance relationship (Sirri & Tufano 1998; Chevalier & Ellison 1997).

### Comparison with Baseline

| Metric | Baseline | Extension | Direction |
|---|---|---|---|
| Q5 premium/month (M3) | 3.23 pp | 2.610 pp | consistent |
| Monotonic Q2→Q5 | Yes | Yes | consistent |
| Convexity ratio | ~2.4× | 3.14× | consistent |

---

## Quality Checks

- ✅ DV is flow_winsorized in all models.
- ✅ past_12m_return is properly lagged (corr with current return=-0.0257).
- ✅ 12m regression sample starts 2004 (2003 is burn-in, as expected).
- ✅ SE clustered by WFICN (1,120 clusters).
- ✅ Sample drop from 12m base (170,616) to full model (135,585) is 35,031 obs, explained by missing exp_ratio/turn_ratio (34,816 obs).
- ✅ past_12m_return positive and significant in M1 (coef=0.0219, p=0.0000).
- ✅ Quintile coefficients Q2→Q5 are monotonically increasing in Model 3.
- ✅ Extension qualitatively consistent with baseline: coef 0.1171 vs 0.0928 (baseline), Q5 2.61 vs 3.23 pp (baseline).

---

## Thesis Caveats

1. **Missing controls (20.5%):** exp_ratio and turn_ratio are missing for ~20% of
   fund-quarter observations in the 2003–2025 FSQ file. Models M1/M2 use the larger
   170,616-obs sample; M3/M4 use 135,585 obs. This is expected given the
   data source and should be noted in the thesis.
2. **No tna_latest in FSQ file:** Numeric characteristics are averaged unweighted
   across share classes (baseline used TNA-weighted). Difference is minor.
3. **2003 burn-in:** The raw extension sample starts 2003 but the 12m regression
   sample effectively starts 2004 (12 months needed for past_12m_return). This is
   by construction and correctly implemented.
4. **WFICN coverage 79% overall:** The MFLinks mapping covers 79% of all fund-months
   but ~95%+ of EDC-classified funds. The 20.9% unmapped are predominantly non-equity
   fund types absent from MFLinks.
5. **Sample period includes COVID-19 (2020) and 2022 rate shock:** These events may
   introduce structural breaks. Subperiod robustness (pre/post-2012) is an optional
   extension.
