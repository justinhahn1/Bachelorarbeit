# 6-Month Robustness Interpretation

## Summary

The 6-month past performance robustness check replicates the main 12-month
flow-performance analysis using `past_6m_return` as the explanatory variable,
both in continuous and quintile form.

---

## Part A: Continuous Regressions

| Model | Coef (6m) | SE | t | p | N | R² |
|---|---|---|---|---|---|---|
| (1) Baseline | +0.0362*** | 0.0018 | 20.38 | 0.0000 | 83,319 | 0.0157 |
| (2) Controls | +0.0358*** | 0.0018 | 20.16 | 0.0000 | 83,319 | 0.0288 |
| (3) Month FE | +0.1319*** | 0.0058 | 22.62 | 0.0000 | 83,319 | 0.0805 |
| (4) Month+EDC FE | +0.1334*** | 0.0058 | 23.05 | 0.0000 | 83,319 | 0.0827 |

### 12m vs 6m Comparison (Model 3, Month FE)

| Specification | Coef | SE | t | p | N |
|---|---|---|---|---|---|
| 12m (past_12m_return) | +0.0928*** | 0.0047 | 19.85 | 0.0000 | 77,140 |
| 6m  (past_6m_return)  | +0.1319*** | 0.0058 | 22.62 | 0.0000 | 83,319 |

**Economic effect of +10 pp past return (Model 3):**
- 12m: +0.928 pp flow change
-  6m: +1.319 pp flow change

The 6m coefficient is larger in absolute terms,
consistent with the shorter performance window capturing more of the flow-relevant signal.
Both are positive and highly significant.

---

## Part B: 6-Month Quintile Analysis

### Average Flows

| Quintile | Mean Flow (pp/month) |
|---|---|
| Q1 (worst) | -1.014 pp |
| Q2 | -0.371 pp |
| Q3 | +0.059 pp |
| Q4 | +0.513 pp |
| Q5 (best) | +1.779 pp |
| **Q5 − Q1 spread** | **+2.792 pp/month** |

### Quintile Regression Coefficients (Model 3)

| Quintile | Coef vs Q1 | SE | t | p | Δflow (pp) |
|---|---|---|---|---|---|
| Q1 (ref.) | 0.0000 | — | — | — | 0.000 |
| Q2 | +0.0064*** | 0.0006 | 10.53 | 0.0000 | +0.640 pp |
| Q3 | +0.0107*** | 0.0007 | 15.91 | 0.0000 | +1.071 pp |
| Q4 | +0.0155*** | 0.0008 | 20.58 | 0.0000 | +1.545 pp |
| Q5 | +0.0286*** | 0.0011 | 25.38 | 0.0000 | +2.861 pp |

**Q5 premium (Model 3):** +2.861 pp/month vs. +3.225 pp/month for 12m sort.

### Monotonicity: YES — monotonically increasing Q2→Q5

### Convexity (Q4→Q5 vs. avg inner step):
- Q4→Q5 step  : +0.0132 (+1.316 pp)
- Avg Q1→Q4   : +0.0052 (+0.515 pp)
- Ratio       : 2.55x → convex pattern (top performers rewarded disproportionately)

---

## Quality Checks

- ✅ DV is flow_winsorized in both Part A and Part B.
- ✅ past_6m_return corr with current return = 0.0435 → no look-ahead bias.
- ✅ 6m sample is larger than 12m by 6,179 obs (expected: shorter horizon needs fewer lags).
- ✅ past_6m_return positive and p<0.01 in all 4 Part A models.
- ✅ Q5 positive and significant in 6m Model 3 (coef=0.0286, p=0.0000).
- ✅ 6m quintile coefficients monotonically increasing in Model 3.
- ✅ 6m results qualitatively consistent with 12m: same sign, both significant.
- ✅ 6m Q5 step (0.0132) disproportionate vs avg Q1–Q4 step (0.0052) → convex pattern.

## Verdict

**THESIS-READY.**
The 6-month robustness check confirms the main 12-month results.
The positive, monotonic, and convex flow-performance relationship is present
in both the continuous and quintile specifications using a 6-month performance window.
