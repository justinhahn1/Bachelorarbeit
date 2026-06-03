**Table A4. Data Diagnostics and Methodological Notes**

**A. WFICN Mapping Coverage**

| Sample | Raw rows | Mapped to WFICN | Mapping rate |
|--------|--------:|----------------:|-------------:|
| Baseline (1991–2011 data) | 1,241,561 | ~1,007,000 | ~81% |
| Extension (2003–2025 data) | 2,115,074 | ~1,673,000 | ~79% |

The ~20% unmapped share consists of non-equity fund classes (bond, money market,
international) that are outside the MFLinks coverage scope. After the EDC filter, the
mapped fraction for EDC-classified funds is ≥95% in both samples.

**B. Sample Restrictions and Their Rationale**

| Restriction | Rationale | Source |
|-------------|-----------|--------|
| EDC classification | Domestic active equity only — ensures homogeneous segment | CRSP crsp_obj_cd |
| Exclude ETF (et_flag + name) | Passive trading vehicles; different flow dynamics | CRSP et_flag |
| Exclude index funds (flag + name) | Passive; remove mechanical inflow patterns | CRSP index_fund_flag |
| Lag TNA ≥ $10M | Remove tiny funds with noisy flows | Chevalier & Ellison (1997); Sirri & Tufano (1998) |
| Flow gap check (28–35 days) | Ensures TNA denominator reflects the same fund over one month | — |
| Winsorise flow 1/99 pct | Removes data errors and extreme outlier months | — |
| Min. 12 monthly returns | Rolling window requires 12 consecutive non-missing returns | — |

**C. Missing Characteristics (Extension)**

In the 2003–2025 fund summary file, `exp_ratio` and `turn_ratio` are jointly missing
for approximately 20.5% of WFICN-quarter observations. This reduces the regression
sample from 170,616 (models M1/M2, past return only or with partial controls)
to 135,585 (models M3/M4, full controls). The pattern is identical in the baseline.
Dropping `turn_ratio` from the model saves only ~215 observations; hence both are
retained for methodological consistency with the baseline.

**D. FSQ Aggregation (Extension Only)**

The 2003–2025 fund summary quarterly file does not contain a `tna_latest` column
(present in the 1991–2011 file). Categorical characteristics are assigned using the
representative share class (lowest `crsp_fundno`, i.e., the oldest class), and numeric
characteristics are averaged unweighted across share classes within each WFICN-quarter.
This is a minor deviation from the baseline's TNA-weighted aggregation; its impact
on the regression coefficients is expected to be negligible given the focus on
fund-level controls.
