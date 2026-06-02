# Final Analysis Overview & QC
## Bachelor Thesis: Fund Flow-Performance Analysis (Active EDC Funds, 1999–2011)

---

## 1. Analysis Pipeline

| Step | Purpose | Input | Output | Sample | Thesis use |
| --- | --- | --- | --- | --- | --- |
| 1 | WFICN-month construction | monthly_returns_1991_2011.csv, mflinks_crsp_fundno_wficn.csv | final_step1_wficn_portfolio_month.csv | 1,241,561 obs | 10,740 WFICN | 1991–2011 | Diagnostic / Appendix |
| 2 | Active EDC filter + flow calc | Step1 + fund_summary_quarterly_1991_2011.csv + fund_portfolio_map | final_step2_clean_wficn_edc_flows.csv | 108,310 obs | 1,322 WFICN | 1999–2011 | Data section |
| 3 | QC cleaning + past performance | Step2 output | final_step3_regression_ready_wficn_edc.csv | 99,325 obs | 1,215 WFICN | 1999–2011 | Data section |
| 4 | 12m continuous regressions | Step3 output | final_step4_main_regressions_12m.{csv,md} | 77,140 obs | 909 WFICN | 2000–2011 | Main text — Results |
| 5 | 12m quintile analysis | Step3 output | final_step5_quintile_{average_flows,regressions}.{csv,md} | 77,140 (reg) | 83,186 (descriptive) | 909–1,121 WFICN | Main text — Results |
| 6 | 6m robustness check | Step3 output | final_step6_robustness_6m_*.{csv,md} | 83,319 (reg) | 90,877 (descriptive) | 957–1,172 WFICN | Appendix / Robustness |

---

## 2. Sample Size Funnel

| Sample stage | N obs | WFICN | From | To |
| --- | --- | --- | --- | --- |
| Step 1 — WFICN-month (all funds) | 1,241,561 | 10,740 | 1991-01-31 | 2011-12-30 |
| Step 2 — Active EDC filtered | 108,310 | 1,322 | 1999-03-31 | 2011-12-30 |
| Step 3 — Regression-ready | 99,325 | 1,215 | 1999-04-30 | 2011-12-30 |
| 12m regression sample (all controls) | 77,140 | 909 | 2000-04-28 | 2011-12-30 |
| 12m quintile sample (DV + IV) | 83,186 | 1,121 | 2000-04-28 | 2011-12-30 |
| 6m regression sample (all controls) | 83,319 | 957 | 1999-10-29 | 2011-12-30 |
| 6m quintile sample (DV + IV) | 90,877 | 1,172 | 1999-10-29 | 2011-12-30 |

**Attrition notes:**
- Step 1 → Step 2: EDC + active fund filter removes ~87% of WFICNs (expected: targeting a narrow fund type)
- Step 2 → Step 3: −8,985 obs from 1 CRSP error, 8,782 tiny-fund filter (lag_tna < $10M), 202 missing flow
- Step 3 → 12m reg sample: −22,185 obs from past_12m_return NaN (needs 12 consecutive months) + exp_ratio/turn_ratio NaN
- Step 3 → 6m reg sample: −15,833 obs; smaller cost because 6m needs only 6 consecutive months
- 6m samples consistently larger than 12m: expected and consistent ✓

---

## 3. Consistency Checks

- ✅ Step1→Step2 WFICN reduction (10,740→1,322, 12.3% kept) reflects EDC+active filter — expected.
- ✅ Step2→Step3: −8,985 obs (8.3%), −107 WFICNs. Explained by: 1 CRSP error, 8,782 tiny-fund filter (lag_tna<$10M), 202 missing flow.
- ✅ Step3→12m quintile sample: −16,139 obs (16.2%). Driven by past_12m_return requiring 12 consecutive months (first available 2000-04).
- ✅ Step3→12m regression sample: additional −6,046 obs from exp_ratio/turn_ratio NaN. turn_ratio alone costs only 169 obs (0.2%).
- ✅ 6m samples larger than 12m (quintile: 90,877 vs 83,186; regression: 83,319 vs 77,140). Expected: 6m needs only 6 consecutive months.
- ✅ All 4 × 12m regression models: N=77,140 (consistent).
- ✅ All 4 × 6m regression models: N=83,319 (consistent).
- ✅ 12m Q5−Q1: raw mean 3.219pp ≈ adj 3.225pp (diff 0.006pp) — controls add little bias.
- ✅ crsp_obj_cd in regression sample: EDCS=46,214, EDCM=26,810, EDCI=4,116 — all EDC-coded, no leakage.
- ✅ flow_winsorized is 100% non-null in Step 3 dataset.

---

## 4. Key Empirical Results

| Specification | Coef | +10 pp → Δflow | R² | N |
| --- | --- | --- | --- | --- |
| 12m continuous (Model 3, Month FE) | 0.0928*** | +0.928 pp/month | 0.0867 | 77,140 |
| 12m quintile Q5 premium (Model 3) | +0.0323*** | Q5−Q1 = +3.23 pp/month | 0.0936 | 77,140 |
| 6m continuous (Model 3, Month FE) | 0.1319*** | +1.319 pp/month | 0.0805 | 83,319 |
| 6m quintile Q5 premium (Model 3) | +0.0286*** | Q5−Q1 = +2.86 pp/month | 0.0784 | 83,319 |

### Summary narrative

All specifications produce the same conclusion: **past performance positively
and significantly predicts fund flows** for active domestic equity (EDC) funds.

- **Continuous regressions:** A 10 pp improvement in past 12-month return is
  associated with +0.93 pp/month more flow (Month FE model), equivalent to
  about 20% of one standard deviation of flows.
- **Quintile analysis:** Flows increase monotonically from Q1 (bottom) to Q5
  (top) in every specification. The Q5 premium over Q1 is +3.23 pp/month
  (regression-adjusted, Month FE). The Q4→Q5 step is **2.4× the average
  Q1–Q4 step**, confirming a **convex (asymmetric) flow-performance
  relationship** — top performers receive disproportionately higher inflows.
- **6-month robustness:** Results are nearly identical in SD-normalised terms
  (0.46 SDs vs 0.48 SDs). Convexity is even stronger (2.9×). All signs and
  significance unchanged.

---

## 5. Thesis Table Inventory

| File | Description | Classification |
| --- | --- | --- |
| final_step2_sample_construction | Sample construction attrition (7 filter steps) | Main text — Data section |
| final_step3_summary_statistics | Summary statistics: regression-ready dataset | Main text — Data section |
| final_step4_main_regressions_12m | Main 12m flow-performance regressions (4 models) | Main text — Results section |
| final_step5_quintile_average_flows | Average flows by 12m performance quintile | Main text — Results section |
| final_step5_quintile_regressions | 12m quintile regressions (4 models, Q1 ref.) | Main text — Results section |
| final_step6_robustness_6m_regressions | 6m robustness: continuous regressions | Main text or Appendix — Robustness section |
| final_step6_robustness_6m_quintile_average_flows | Average flows by 6m performance quintile | Appendix |
| final_step6_robustness_6m_quintile_regressions | 6m quintile regressions | Appendix |
| final_step1_wficn_mapping_diagnostics | WFICN mapping coverage by year (1991–2011) | Appendix |
| final_step2_return_flow_quality_check | Return and flow outlier diagnostics | Appendix or diagnostic only |
| final_step4_regression_qc_check | Regression specification QC checks | Diagnostic only |
| final_step2_quality_checks | Step 2 quality checks | Diagnostic only |
| final_step3_sample_construction | Step 3 QC cleaning attrition | Appendix footnote |

---

## 6. Caveats to Mention in Thesis

### 1. Portfolio identifier: WFICN not crsp_portno
crsp_portno coverage is sparse before 2003 in the fund_portfolio_map. WFICN (MFLinks) is static but achieves 93–99% mapping coverage across 1991–2011. One WFICN can span multiple crsp_portnos due to fund restructurings; modal WFICN used for multi-mapped fundnos.

### 2. Effective sample start 1999-03, not 1997
The Fund Summary file (crsp_obj_cd) only covers from 1999-03-31, so EDC classification is unavailable before that date. The intended 1997 start cannot be achieved without a different classification source.

### 3. Past performance: raw returns, not alpha
Past 12m and 6m returns are cumulative log-space raw returns, not risk-adjusted (no Fama-French alpha, no Sharpe ratio). This is consistent with investor-level flow-chasing behaviour, where investors react to reported returns rather than alpha. Robustness with alpha is a possible extension.

### 4. Active EDC funds only
The sample covers only small/mid-cap domestic equity core funds (EDCS, EDCM, EDCI). Results may not generalise to large-cap, growth, value, or international equity categories. No Morningstar categories used.

### 5. Minimum TNA filter: lag_portfolio_tna ≥ $10M
Removes 8,782 obs (8.1% of Step 2 sample, 107 WFICNs). Standard in the literature to avoid extreme flow artefacts from tiny funds. Sensitivity to this threshold is a possible robustness check.

### 6. Winsorized flows at 1st/99th percentile
Raw flow can reach +813% (tiny lagged TNA). Winsorizing at 1/99 is standard. Raw flow range in Step 2: [−104.5%, +813.4%]; after winsorizing [−17.8%, +28.9%]. The 1 CRSP error obs (mret=12,012) is dropped separately.

### 7. OLS with WFICN-clustered SEs throughout
No fund fixed effects (within-WFICN variation in performance is the source of identification). No Fama-MacBeth (FMB) as an alternative. FMB would give time-series average coefficients; pooled OLS with month FE is used instead, which is standard in this literature.

### 8. No subperiod analysis by default
The 2008–2009 financial crisis sits in the middle of the sample and may create different flow-performance dynamics. A pre/post-2008 split is a natural extension if the supervisor requests it.

---

## 7. What Is Still Open

### 1. OPTIONAL — Subperiod analysis
Split 2000–2007 vs 2008–2011 (or 2000–2008 vs 2009–2011). Straightforward to add if supervisor requests it. Code would replicate final_step5_regressions.py with a year filter.

### 2. OPTIONAL — Fama-MacBeth alternative
Some supervisors prefer FMB over pooled OLS + month FE for cross-sectional regressions. Available via linearmodels.FamaMacBeth.

### 3. OPTIONAL — Risk-adjusted performance
Replace past_12m_return with 12m Fama-French 3-factor alpha. Requires daily factor data already present in the repo.

### 4. REQUIRED — Jupyter notebook consolidation
Consolidate all final_step*.py scripts into a single bachelorthesis_final.ipynb with narrative, tables, and figures. This is the deliverable for the thesis.

### 5. REQUIRED — Write-up: Data & Sample section
Describe the three CRSP source files, MFLinks mapping, EDC filter, sample period, and QC rules. Reference final_step2_sample_construction.

### 6. REQUIRED — Write-up: Methodology section
Define flow formula, past_12m_return construction, quintile assignment, regression models, fixed effects, and clustering. Cite Sirri & Tufano (1998), Chevalier & Ellison (1997), Barber et al. (2022).

### 7. REQUIRED — Write-up: Results section
Table: main 12m regressions. Table: quintile average flows + regressions. Paragraph: robustness (6m). Paragraph: convexity finding. One figure (optional): quintile bar chart.

---

## 8. Final Verdict

**Coherence:** YES — all consistency checks pass. No unexplained discrepancies.

**Main tables thesis-ready:** YES.
- Main 12m regression table: thesis-ready (all 4 models, WFICN-clustered SEs, correct DV/IV)
- Quintile tables: thesis-ready (monotone, convex, robust to controls and FE)
- 6m robustness: thesis-ready (confirms main finding, labelled as robustness)
- Summary statistics: thesis-ready (standard format)
- Sample construction: thesis-ready (7-step attrition table)

**Subperiod analysis:** OPTIONAL. Not needed for the main argument, but easy
to add if the supervisor asks about the 2008 crisis impact. One additional
model column per table would suffice.

**Jupyter notebook consolidation:** REQUIRED as the final deliverable.
All analysis scripts are complete and verified. The next step is to
assemble them into `bachelorthesis_final.ipynb` with narrative text,
formatted tables, and (optionally) a quintile bar chart figure.

**Project status: ✅ Empirical analysis complete. Ready for write-up.**
