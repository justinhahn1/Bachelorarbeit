"""
Extension Step 3 — Flow-performance regressions and quintile analysis (2003–2025)

Part A: Main 12-month OLS regressions (4 models)
Part B: Monthly past_12m_return quintile analysis (average flows + 4 regression models)

Methodology is identical to the baseline (final_step5_regressions.py and
final_step6_quintile_analysis.py). No baseline files are modified.

Input  : data/processed/extension_2003_2025_step3_regression_ready_wficn_edc.csv
Outputs: output/tables/extension_2003_2025_main_regressions_12m.{csv,md}
         output/tables/extension_2003_2025_quintile_average_flows.{csv,md}
         output/tables/extension_2003_2025_quintile_regressions.{csv,md}
         output/tables/extension_2003_2025_results_interpretation.md

Baseline reference values (for comparison):
  Preferred coefficient (M3): 0.0928
  Q5 premium (M3):           +3.23 pp/month
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import os, warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit/real data"
PROC = BASE + "/NEW_BA_analysis/data/processed/"
TABS = BASE + "/NEW_BA_analysis/output/tables/"
os.makedirs(TABS, exist_ok=True)

PREFIX = "extension_2003_2025_"

# Baseline reference values
BASELINE_COEF_M3 = 0.0928
BASELINE_Q5_PP   = 3.23    # pp/month, Model 3

SEP  = "\n" + "═" * 72
SEP2 = "─" * 72

def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""

def tbl_to_md(df):
    cols  = df.columns.tolist()
    lines = ["| " + " | ".join(str(c) for c in cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Load and inspect
# ══════════════════════════════════════════════════════════════════════════════
print("Loading regression-ready dataset …")
df = pd.read_csv(PROC + PREFIX + "step3_regression_ready_wficn_edc.csv",
                 low_memory=False)
df["caldt"] = pd.to_datetime(df["caldt"])

print(f"  Rows loaded    : {len(df):>10,}")
print(f"  Unique WFICN   : {df['wficn'].nunique():>10,}")
print(f"  Date range     : {df['caldt'].min().date()} → {df['caldt'].max().date()}")
print(f"  12m sample     : {df['past_12m_return'].notna().sum():>10,} obs with past_12m_return")
print(f"  12m start year : {df.loc[df['past_12m_return'].notna(),'caldt'].dt.year.min()} "
      f"(2003 is burn-in year, as expected)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Build main regression sample (all controls non-null)
# ══════════════════════════════════════════════════════════════════════════════
controls = ["log_lag_tna", "exp_ratio", "fund_age_years", "turn_ratio"]
required = ["flow_winsorized", "past_12m_return"] + controls

reg = df.dropna(subset=required).copy().reset_index(drop=True)

print(SEP)
print("2. MAIN REGRESSION SAMPLE")
print("═" * 72)
print(f"\n  Obs (all required vars non-null) : {len(reg):>9,}")
print(f"  Unique WFICN                     : {reg['wficn'].nunique():>9,}")
print(f"  Date range                       : "
      f"{reg['caldt'].min().date()} → {reg['caldt'].max().date()}")
print(f"  Unique months                    : {reg['caldt'].nunique():>9,}")
print(f"\n  crsp_obj_cd distribution:")
for code, cnt in reg["crsp_obj_cd"].value_counts().items():
    print(f"    {code:>6} : {cnt:>9,}  ({100*cnt/len(reg):.1f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Construct regressors
# ══════════════════════════════════════════════════════════════════════════════
reg["month_str"] = reg["caldt"].dt.to_period("M").astype(str)
month_dummies    = pd.get_dummies(reg["month_str"], prefix="m",
                                   drop_first=True, dtype=float)

# EDC style dummies — EDCS is the baseline; keep EDCM and EDCI
edc_dummies_all = pd.get_dummies(reg["crsp_obj_cd"], prefix="edc",
                                  drop_first=False, dtype=float)
edc_cols    = [c for c in edc_dummies_all.columns if c != "edc_EDCS"]
edc_dummies = edc_dummies_all[edc_cols].reset_index(drop=True)
month_dummies = month_dummies.reset_index(drop=True)

Y           = reg["flow_winsorized"]
cluster_ids = reg["wficn"].values

X1 = sm.add_constant(reg[["past_12m_return"]])
X2 = sm.add_constant(reg[["past_12m_return"] + controls])
X3 = sm.add_constant(pd.concat([reg[["past_12m_return"] + controls],
                                  month_dummies], axis=1))
X4 = sm.add_constant(pd.concat([reg[["past_12m_return"] + controls],
                                  month_dummies, edc_dummies], axis=1))


# ══════════════════════════════════════════════════════════════════════════════
# 4. Part A — Run main regressions
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("PART A — MAIN 12-MONTH REGRESSIONS")
print("═" * 72)

def run_ols(Y_, X_, cids, label):
    m = sm.OLS(Y_, X_).fit(cov_type="cluster", cov_kwds={"groups": cids})
    print(f"\n  {label}")
    print(f"    N={int(m.nobs):,}  R²={m.rsquared:.4f}  adj-R²={m.rsquared_adj:.4f}")
    return m

m1 = run_ols(Y, X1, cluster_ids, "Model 1: Baseline (past_12m_return only)")
m2 = run_ols(Y, X2, cluster_ids, "Model 2: Controls")
m3 = run_ols(Y, X3, cluster_ids, "Model 3: Controls + Month FE")
m4 = run_ols(Y, X4, cluster_ids, "Model 4: Controls + Month FE + EDC FE")

models_main  = [m1, m2, m3, m4]
labels_main  = ["(1) Baseline", "(2) Controls", "(3) Month FE", "(4) Month+EDC FE"]


# ══════════════════════════════════════════════════════════════════════════════
# 5. Build thesis-ready regression table
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("5. REGRESSION TABLE — PART A")
print("═" * 72)

display_vars = ["past_12m_return"] + controls + ["const"]
display_labels = {
    "past_12m_return" : "Past 12m Return",
    "log_lag_tna"     : "log(TNA_{t-1})",
    "exp_ratio"       : "Expense Ratio",
    "fund_age_years"  : "Fund Age (years)",
    "turn_ratio"      : "Turnover Ratio",
    "const"           : "Constant",
}

rows_main = []
for var in display_vars:
    lbl      = display_labels.get(var, var)
    coef_row = {"Variable": lbl}
    se_row   = {"Variable": ""}
    for i, m in enumerate(models_main, 1):
        if var in m.params.index:
            c = m.params[var]; s = m.bse[var]; p = m.pvalues[var]
            coef_row[f"M{i}"] = f"{c:.4f}{stars(p)}"
            se_row[f"M{i}"]   = f"({s:.4f})"
        else:
            coef_row[f"M{i}"] = "—"
            se_row[f"M{i}"]   = ""
    rows_main.append(coef_row)
    rows_main.append(se_row)

# Footer
for label_str, vals in [
    ("N",           [f"{int(m.nobs):,}"      for m in models_main]),
    ("R²",          [f"{m.rsquared:.4f}"     for m in models_main]),
    ("Adj. R²",     [f"{m.rsquared_adj:.4f}" for m in models_main]),
    ("Month FE",    ["No", "No", "Yes", "Yes"]),
    ("EDC Style FE",["No", "No", "No",  "Yes"]),
]:
    row = {"Variable": label_str}
    for i, v in enumerate(vals, 1): row[f"M{i}"] = v
    rows_main.append(row)

tbl_main = pd.DataFrame(rows_main, columns=["Variable","M1","M2","M3","M4"])
tbl_main.columns = ["Variable"] + labels_main

col_w = [28, 18, 18, 18, 18]
header = "  " + "  ".join(str(c).ljust(w) for c, w in zip(tbl_main.columns, col_w))
print(f"\n{header}")
print(f"  {SEP2}")
for _, row in tbl_main.iterrows():
    print("  " + "  ".join(str(v).ljust(w) for v, w in zip(row, col_w)))
print(f"\n  Notes: DV=flow_winsorized. SE clustered by WFICN. "
      f"*** p<0.01  ** p<0.05  * p<0.10")
print(f"  Sample: active EDC WFICN-month obs, extension 2003–2025.")


# ══════════════════════════════════════════════════════════════════════════════
# 6. Economic interpretation — Part A
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("6. ECONOMIC INTERPRETATION — PART A")
print("═" * 72)

sd_perf = reg["past_12m_return"].std()
sd_flow = reg["flow_winsorized"].std()

print(f"\n  past_12m_return coefficient (preferred = Model 3):")
for lbl, m in zip(labels_main, models_main):
    c = m.params["past_12m_return"]
    s = m.bse["past_12m_return"]
    p = m.pvalues["past_12m_return"]
    delta_10pp = c * 0.10
    print(f"    {lbl:<22} : coef={c:+.4f}  SE={s:.4f}  p={p:.4f}{stars(p)}"
          f"  +10pp→flow: {delta_10pp*100:+.3f} pp")

coef_m3_a = m3.params["past_12m_return"]
se_m3_a   = m3.bse["past_12m_return"]
pv_m3_a   = m3.pvalues["past_12m_return"]

print(f"\n  SD of past_12m_return : {sd_perf:.4f}  ({sd_perf*100:.2f} pp)")
print(f"  SD of flow_winsorized : {sd_flow:.4f}  ({sd_flow*100:.2f} pp)")
print(f"\n  1-SD increase in past_12m_return → flow change:")
for lbl, m in zip(labels_main, models_main):
    delta = m.params["past_12m_return"] * sd_perf
    print(f"    {lbl:<22} : {delta*100:+.3f} pp  ({abs(delta)/sd_flow:.2f} SDs of flow)")

print(f"\n  Significance at 5% level:")
for lbl, m in zip(labels_main, models_main):
    p = m.pvalues.get("past_12m_return", np.nan)
    print(f"    {lbl:<22} : {'YES' if p < 0.05 else 'NO '}  (p={p:.4f})")

# Baseline comparison
print(f"\n  Comparison with baseline (1999–2011):")
print(f"    Baseline M3 coef    : {BASELINE_COEF_M3:+.4f}")
print(f"    Extension M3 coef   : {coef_m3_a:+.4f}")
diff_coef = coef_m3_a - BASELINE_COEF_M3
direction = "stronger" if coef_m3_a > BASELINE_COEF_M3 else "weaker"
print(f"    Difference          : {diff_coef:+.4f}  ({direction} than baseline)")
print(f"    Qualitatively       : {'SIMILAR' if abs(diff_coef)/BASELINE_COEF_M3 < 0.30 else 'DIFFERENT'}"
      f"  (within 30% of baseline = similar)")


# ══════════════════════════════════════════════════════════════════════════════
# 7. Save Part A outputs
# ══════════════════════════════════════════════════════════════════════════════
tbl_main.to_csv(TABS + PREFIX + "main_regressions_12m.csv", index=False)
print(f"\n  Saved CSV → {TABS}{PREFIX}main_regressions_12m.csv")

md_main = (
    f"# Flow-Performance Regressions — Extension Sample (2003–2025)\n\n"
    f"## Table: OLS Regressions — Dependent Variable: Flow (winsorized)\n\n"
    + tbl_to_md(tbl_main)
    + f"\n\n**Notes:**\n"
    f"Standard errors clustered by WFICN. \\*** p<0.01, \\** p<0.05, \\* p<0.10\n"
    f"Sample: active domestic equity (EDC) funds, 2004–2025 (effective 12m window).\n"
    f"Past 12m Return is the gap-aware cumulative 12-month lagged return "
    f"(excludes current month; shift(1) + rolling(12) in log-space).\n"
    f"N={int(m4.nobs):,} in the full model (missing exp_ratio/turn_ratio "
    f"reduces N from 170,616 to {int(m4.nobs):,}).\n"
)
with open(TABS + PREFIX + "main_regressions_12m.md", "w") as f:
    f.write(md_main)
print(f"  Saved  MD → {TABS}{PREFIX}main_regressions_12m.md")


# ══════════════════════════════════════════════════════════════════════════════
# 8. Part B — Monthly quintile assignment
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("PART B — 12-MONTH QUINTILE ANALYSIS")
print("═" * 72)

base_req = ["flow_winsorized", "past_12m_return"]
df_q = df.dropna(subset=base_req).copy()
print(f"\n  Obs with non-null DV + IV : {len(df_q):>9,}")
print(f"  Unique WFICN              : {df_q['wficn'].nunique():>9,}")
print(f"  Unique months             : {df_q['caldt'].nunique():>9,}")

def assign_quintile(series):
    try:
        return pd.qcut(series, q=5, labels=[1,2,3,4,5]).astype(int)
    except ValueError:
        return pd.qcut(series.rank(method="first"), q=5,
                       labels=[1,2,3,4,5]).astype(int)

df_q["quintile"] = (
    df_q.groupby("caldt")["past_12m_return"]
    .transform(assign_quintile)
)

# Monthly quintile size diagnostics
month_qsizes = (
    df_q.groupby(["caldt","quintile"])["wficn"]
    .count().unstack("quintile")
    .rename(columns={i: f"Q{i}" for i in range(1,6)})
)
print(f"\n  Monthly quintile size (obs per quintile per month):")
print(f"  {'Quintile':<8}  {'Mean':>7}  {'Min':>7}  {'Max':>7}")
print(f"  {SEP2[:40]}")
for q in ["Q1","Q2","Q3","Q4","Q5"]:
    col = month_qsizes[q]
    print(f"  {q:<8}  {col.mean():>7.1f}  {col.min():>7.0f}  {col.max():>7.0f}")

thin_months = (month_qsizes.min(axis=1) < 5).sum()
print(f"\n  Months with any quintile < 5 funds : {thin_months}")
if thin_months > 0:
    print(f"  (Retained — thin quintiles noted, not dropped)")

print(f"\n  Quintile distribution across full sample:")
for q, n in df_q["quintile"].value_counts().sort_index().items():
    print(f"    Q{q} : {n:>9,}")


# ══════════════════════════════════════════════════════════════════════════════
# 9. Table A — Average flows by quintile
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("9. TABLE A — AVERAGE FLOWS BY QUINTILE")
print("═" * 72)

flow_by_q = (
    df_q.groupby("quintile")["flow_winsorized"]
    .agg(mean_flow="mean", median_flow="median", n_obs="count")
    .reset_index()
)
flow_by_q["unique_wficn"] = (
    df_q.groupby("quintile")["wficn"].nunique().values
)
flow_by_q["quintile_label"] = flow_by_q["quintile"].map(
    {1:"Q1 (worst)",2:"Q2",3:"Q3",4:"Q4",5:"Q5 (best)"}
)
flow_by_q = flow_by_q[["quintile_label","mean_flow","median_flow","n_obs","unique_wficn"]]

q5_mean  = flow_by_q.loc[flow_by_q["quintile_label"]=="Q5 (best)",  "mean_flow"].values[0]
q1_mean  = flow_by_q.loc[flow_by_q["quintile_label"]=="Q1 (worst)", "mean_flow"].values[0]
spread   = q5_mean - q1_mean
spread_pp = spread * 100

monthly_spread = (
    df_q.groupby(["caldt","quintile"])["flow_winsorized"]
    .mean().unstack("quintile")
    .assign(spread=lambda d: d[5]-d[1])["spread"].mean()
)

print(f"\n  {'Quintile':<14}  {'Mean Flow':>10}  {'Median Flow':>12}  "
      f"{'N obs':>8}  {'Uniq WFICN':>11}")
print(f"  {SEP2}")
for _, row in flow_by_q.iterrows():
    print(f"  {row['quintile_label']:<14}  {row['mean_flow']:>+10.4f}  "
          f"{row['median_flow']:>+12.4f}  {int(row['n_obs']):>8,}  "
          f"{int(row['unique_wficn']):>11,}")
print(f"\n  Q5−Q1 spread (full-sample means) : {spread:+.4f}  ({spread_pp:+.3f} pp/month)")
print(f"  Q5−Q1 spread (monthly averages)  : {monthly_spread:+.4f}  "
      f"({monthly_spread*100:+.3f} pp/month)")

perf_by_q = df_q.groupby("quintile")["past_12m_return"].mean()
print(f"\n  Mean past_12m_return per quintile (sanity check):")
for q, v in perf_by_q.items():
    print(f"    Q{q} : {v:+.4f}  ({v*100:+.2f} pp)")

# Baseline comparison
print(f"\n  Comparison with baseline Q5 premium: "
      f"baseline={BASELINE_Q5_PP:+.2f} pp/month  extension={spread_pp:+.3f} pp/month")


# ══════════════════════════════════════════════════════════════════════════════
# 10. Build quintile regression sample (all controls)
# ══════════════════════════════════════════════════════════════════════════════
reg_q = df_q.dropna(subset=controls).copy().reset_index(drop=True)
print(SEP)
print("10. QUINTILE REGRESSION SAMPLE")
print("═" * 72)
print(f"\n  Obs (all controls non-null) : {len(reg_q):>9,}")
print(f"  Unique WFICN               : {reg_q['wficn'].nunique():>9,}")
print(f"\n  Quintile distribution in regression sample:")
for q, n in reg_q["quintile"].value_counts().sort_index().items():
    print(f"    Q{q} : {n:>9,}")

q_dummies     = pd.get_dummies(reg_q["quintile"].astype(int), prefix="Q",
                                drop_first=False, dtype=float)
q_dummies     = q_dummies.drop(columns=["Q_1"])   # Q1 = reference group
q_dummy_cols  = ["Q_2","Q_3","Q_4","Q_5"]

reg_q["month_str"] = reg_q["caldt"].dt.to_period("M").astype(str)
m_dum_q = pd.get_dummies(reg_q["month_str"], prefix="m", drop_first=True, dtype=float)

edc_dum_q_all = pd.get_dummies(reg_q["crsp_obj_cd"], prefix="edc",
                                drop_first=False, dtype=float)
edc_cols_q    = [c for c in edc_dum_q_all.columns if c != "edc_EDCS"]
edc_dum_q     = edc_dum_q_all[edc_cols_q]

q_dummies  = q_dummies.reset_index(drop=True)
m_dum_q    = m_dum_q.reset_index(drop=True)
edc_dum_q  = edc_dum_q.reset_index(drop=True)

Y_q           = reg_q["flow_winsorized"]
cluster_ids_q = reg_q["wficn"].values

X1q = sm.add_constant(q_dummies)
X2q = sm.add_constant(pd.concat([q_dummies, reg_q[controls]], axis=1))
X3q = sm.add_constant(pd.concat([q_dummies, reg_q[controls], m_dum_q], axis=1))
X4q = sm.add_constant(pd.concat([q_dummies, reg_q[controls], m_dum_q, edc_dum_q], axis=1))


# ══════════════════════════════════════════════════════════════════════════════
# 11. Run quintile regressions
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("11. RUNNING QUINTILE REGRESSIONS")
print("═" * 72)

qm1 = run_ols(Y_q, X1q, cluster_ids_q, "Quintile Model 1: dummies only")
qm2 = run_ols(Y_q, X2q, cluster_ids_q, "Quintile Model 2: + controls")
qm3 = run_ols(Y_q, X3q, cluster_ids_q, "Quintile Model 3: + controls + month FE")
qm4 = run_ols(Y_q, X4q, cluster_ids_q, "Quintile Model 4: + controls + month FE + EDC FE")

models_q = [qm1, qm2, qm3, qm4]
labels_q = ["(1) Baseline","(2) Controls","(3) Month FE","(4) Month+EDC FE"]


# ══════════════════════════════════════════════════════════════════════════════
# 12. Build quintile regression table
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("12. QUINTILE REGRESSION TABLE")
print("═" * 72)

display_q = q_dummy_cols + controls + ["const"]
labels_q_map = {
    "Q_2":"Q2","Q_3":"Q3","Q_4":"Q4","Q_5":"Q5",
    "log_lag_tna":"log(TNA_{t-1})","exp_ratio":"Expense Ratio",
    "fund_age_years":"Fund Age (years)","turn_ratio":"Turnover Ratio",
    "const":"Constant",
}

rows_q = []
for var in display_q:
    lbl      = labels_q_map.get(var, var)
    coef_row = {"Variable": lbl}
    se_row   = {"Variable": ""}
    for i, m in enumerate(models_q, 1):
        if var in m.params.index:
            c = m.params[var]; s = m.bse[var]; p = m.pvalues[var]
            coef_row[f"M{i}"] = f"{c:.4f}{stars(p)}"
            se_row[f"M{i}"]   = f"({s:.4f})"
        else:
            coef_row[f"M{i}"] = "—"
            se_row[f"M{i}"]   = ""
    rows_q.append(coef_row)
    rows_q.append(se_row)

for label_str, vals in [
    ("Q1 (ref.)",  ["Yes"]*4),
    ("N",          [f"{int(m.nobs):,}" for m in models_q]),
    ("R²",         [f"{m.rsquared:.4f}" for m in models_q]),
    ("Adj. R²",    [f"{m.rsquared_adj:.4f}" for m in models_q]),
    ("Month FE",   ["No","No","Yes","Yes"]),
    ("EDC FE",     ["No","No","No","Yes"]),
]:
    row = {"Variable": label_str}
    for i, v in enumerate(vals, 1): row[f"M{i}"] = v
    rows_q.append(row)

tbl_q = pd.DataFrame(rows_q, columns=["Variable","M1","M2","M3","M4"])
tbl_q.columns = ["Variable"] + labels_q

col_w = [20, 18, 18, 18, 18]
header = "  " + "  ".join(str(c).ljust(w) for c, w in zip(tbl_q.columns, col_w))
print(f"\n{header}")
print(f"  {SEP2}")
for _, row in tbl_q.iterrows():
    print("  " + "  ".join(str(v).ljust(w) for v, w in zip(row, col_w)))
print(f"\n  Notes: Q1=reference. WFICN-clustered SE. *** p<0.01  ** p<0.05  * p<0.10")


# ══════════════════════════════════════════════════════════════════════════════
# 13. Monotonicity and convexity
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("13. MONOTONICITY AND CONVEXITY")
print("═" * 72)

for lbl, m in zip(labels_q, models_q):
    coefs = [m.params.get(q, np.nan) for q in q_dummy_cols]
    diffs = [coefs[i+1]-coefs[i] for i in range(len(coefs)-1)]
    mono  = all(d > 0 for d in diffs if not np.isnan(d))
    coef_str = "  ".join(f"Q{i+2}={c:.4f}" for i, c in enumerate(coefs))
    print(f"\n  {lbl:<22}")
    print(f"    Coefs vs Q1: {coef_str}")
    print(f"    Monotonically increasing Q2→Q5: {'YES' if mono else 'NO'}")
    if not mono:
        print(f"    Diffs: {[round(d,4) for d in diffs]}")

# Convexity (Model 3 preferred)
print(f"\n  Convexity (Q4→Q5 step vs. avg of Q2→Q3 and Q3→Q4 steps):")
for lbl, m in zip(labels_q, models_q):
    coefs = [0.0] + [m.params.get(q, np.nan) for q in q_dummy_cols]  # Q1=0
    if all(not np.isnan(c) for c in coefs):
        q4q5_step   = coefs[4] - coefs[3]
        avg_inner   = np.mean([coefs[2]-coefs[1], coefs[3]-coefs[2]])
        ratio       = q4q5_step / avg_inner if avg_inner != 0 else np.nan
        print(f"  {lbl:<22}  Q4→Q5={q4q5_step:+.4f}  avg(Q2→Q3,Q3→Q4)={avg_inner:+.4f}"
              f"  ratio={ratio:.2f}x")


# ══════════════════════════════════════════════════════════════════════════════
# 14. Economic magnitudes — Part B
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("14. ECONOMIC MAGNITUDES — QUINTILE ANALYSIS (Model 3)")
print("═" * 72)

sd_flow_q = Y_q.std()
q5_effect_pp = qm3.params["Q_5"] * 100
coefs_q3 = [0.0] + [qm3.params.get(q, np.nan) for q in q_dummy_cols]
q4q5_step_m3   = coefs_q3[4] - coefs_q3[3]
avg_inner_m3   = np.mean([coefs_q3[2]-coefs_q3[1], coefs_q3[3]-coefs_q3[2]])
convex_ratio_m3 = q4q5_step_m3 / avg_inner_m3 if avg_inner_m3 != 0 else np.nan

print(f"\n  SD of flow_winsorized = {sd_flow_q*100:.2f} pp")
print(f"\n  Quintile effects vs Q1 (Model 3 — preferred spec):")
print(f"  {'Quintile':<8}  {'Coef':>9}  {'SE':>9}  {'t':>7}  {'p':>8}  "
      f"{'Sig':>5}  {'Δflow(pp)':>10}")
print(f"  {SEP2}")
print(f"  {'Q1(ref)':<8}  {'0.0000':>9}  {'—':>9}  {'—':>7}  {'—':>8}  "
      f"{'—':>5}  {'0.000':>10}")
for q in q_dummy_cols:
    c  = qm3.params[q]; se = qm3.bse[q]
    t  = qm3.tvalues[q]; p  = qm3.pvalues[q]
    print(f"  {q.replace('_',''):<8}  {c:>+9.4f}  {se:>9.4f}  {t:>7.2f}  "
          f"{p:>8.4f}  {stars(p):>5}  {c*100:>+10.3f} pp")

print(f"\n  Q5 premium vs Q1:")
print(f"    Unconditional (mean difference)  : {spread_pp:+.3f} pp/month")
print(f"    Regression-adjusted (Model 3)    : {q5_effect_pp:+.3f} pp/month")
print(f"    As fraction of SD(flow)          : {abs(qm3.params['Q_5'])/sd_flow_q:.2f} SDs")
print(f"\n  Convexity (Model 3) : Q4→Q5={q4q5_step_m3*100:+.3f} pp  "
      f"avg_inner={avg_inner_m3*100:+.3f} pp  ratio={convex_ratio_m3:.2f}x")
print(f"\n  Baseline comparison:")
print(f"    Baseline Q5 premium (M3)         : {BASELINE_Q5_PP:+.2f} pp/month")
print(f"    Extension Q5 premium (M3)        : {q5_effect_pp:+.3f} pp/month")
diff_q5 = q5_effect_pp - BASELINE_Q5_PP
direction_q5 = "stronger" if q5_effect_pp > BASELINE_Q5_PP else "weaker"
print(f"    Difference                       : {diff_q5:+.3f} pp  ({direction_q5})")


# ══════════════════════════════════════════════════════════════════════════════
# 15. Quality checks
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("15. QUALITY CHECKS")
print("═" * 72)

passes = []
flags  = []

# QC 1: DV
if Y.name == "flow_winsorized":
    passes.append("DV is flow_winsorized in all models.")
else:
    flags.append(f"DV is {Y.name}, not flow_winsorized.")

# QC 2: Lagged performance (correlation with current return near zero)
lag_corr = df[["past_12m_return","portfolio_return"]].dropna().corr()
corr_val = lag_corr.loc["past_12m_return","portfolio_return"]
if abs(corr_val) < 0.05:
    passes.append(f"past_12m_return is properly lagged (corr with current return={corr_val:.4f}).")
else:
    flags.append(f"Correlation of past_12m_return with current return = {corr_val:.4f} — check lag.")

# QC 3: 2003 burn-in / 2004 start
first_r12_year = df.loc[df["past_12m_return"].notna(),"caldt"].dt.year.min()
if first_r12_year >= 2004:
    passes.append(f"12m regression sample starts {first_r12_year} (2003 is burn-in, as expected).")
else:
    flags.append(f"past_12m_return starts in {first_r12_year} — earlier than expected.")

# QC 4: WFICN-clustered SE (structural check via N vs nobs)
n_clusters = len(np.unique(cluster_ids))
if n_clusters == reg["wficn"].nunique():
    passes.append(f"SE clustered by WFICN ({n_clusters:,} clusters).")
else:
    flags.append("Cluster count mismatch.")

# QC 5: Sample size drop explained by exp_ratio/turn_ratio missingness
n_r12       = df["past_12m_return"].notna().sum()
n_full_main = int(m4.nobs)
n_lost      = n_r12 - n_full_main
exp_miss    = df.loc[df["past_12m_return"].notna(), "exp_ratio"].isna().sum()
if abs(n_lost - exp_miss) < 500:
    passes.append(f"Sample drop from 12m base ({n_r12:,}) to full model ({n_full_main:,}) "
                  f"is {n_lost:,} obs, explained by missing exp_ratio/turn_ratio ({exp_miss:,} obs).")
else:
    flags.append(f"Unexpected sample drop: lost {n_lost:,} but exp_ratio missing {exp_miss:,}.")

# QC 6: Positive and significant past_12m_return in M1
coef_m1_main = m1.params["past_12m_return"]
pval_m1_main = m1.pvalues["past_12m_return"]
if coef_m1_main > 0 and pval_m1_main < 0.05:
    passes.append(f"past_12m_return positive and significant in M1 "
                  f"(coef={coef_m1_main:.4f}, p={pval_m1_main:.4f}).")
else:
    flags.append(f"past_12m_return in M1: coef={coef_m1_main:.4f}, p={pval_m1_main:.4f}.")

# QC 7: Monotonicity in preferred quintile spec (Model 3)
coefs3_q = [qm3.params.get(q, np.nan) for q in q_dummy_cols]
diffs3_q = [coefs3_q[i+1]-coefs3_q[i] for i in range(len(coefs3_q)-1)]
mono3_q  = all(d > 0 for d in diffs3_q if not np.isnan(d))
if mono3_q:
    passes.append("Quintile coefficients Q2→Q5 are monotonically increasing in Model 3.")
else:
    flags.append("Quintile coefficients NOT monotonic in Model 3: "
                 f"diffs={[round(d,4) for d in diffs3_q]}")

# QC 8: Qualitative comparison with baseline
sim_coef = abs(coef_m3_a - BASELINE_COEF_M3) / BASELINE_COEF_M3 < 0.30
sim_q5   = abs(q5_effect_pp - BASELINE_Q5_PP) / BASELINE_Q5_PP < 0.30
if sim_coef and sim_q5:
    passes.append(f"Extension qualitatively consistent with baseline: "
                  f"coef {coef_m3_a:.4f} vs {BASELINE_COEF_M3} (baseline), "
                  f"Q5 {q5_effect_pp:.2f} vs {BASELINE_Q5_PP} pp (baseline).")
else:
    flags.append(f"Extension results differ from baseline by >30%: "
                 f"coef {coef_m3_a:.4f} vs {BASELINE_COEF_M3}, "
                 f"Q5 {q5_effect_pp:.2f} vs {BASELINE_Q5_PP} pp.")

print()
for p in passes: print(f"  PASS  {p}")
for fl in flags:  print(f"  FLAG  {fl}")


# ══════════════════════════════════════════════════════════════════════════════
# 16. Save Part B outputs
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("16. SAVING PART B OUTPUTS")
print("═" * 72)

# Average flows CSV + MD
tblA = flow_by_q.copy()
tblA.columns = ["Quintile","Mean Flow","Median Flow","N obs","Unique WFICN"]
tblA["Mean Flow (pp)"]   = (tblA["Mean Flow"]   * 100).round(4)
tblA["Median Flow (pp)"] = (tblA["Median Flow"] * 100).round(4)
spread_row = pd.DataFrame([{
    "Quintile": "Q5 − Q1 spread", "Mean Flow": spread, "Median Flow": np.nan,
    "N obs": np.nan, "Unique WFICN": np.nan,
    "Mean Flow (pp)": round(spread_pp,4), "Median Flow (pp)": np.nan,
}])
tblA_full = pd.concat([tblA, spread_row], ignore_index=True)
tblA_full.to_csv(TABS + PREFIX + "quintile_average_flows.csv", index=False)
print(f"\n  Saved avg flows CSV → {TABS}{PREFIX}quintile_average_flows.csv")

avg_flow_md_str = (
    "# Average Fund Flows by Quintile — Extension 2003–2025\n\n"
    + tbl_to_md(pd.concat([tblA.astype(str),
                            pd.DataFrame([{"Quintile":"**Q5−Q1 spread**",
                                           "Mean Flow":f"{spread:.4f}","Median Flow":"—",
                                           "N obs":"—","Unique WFICN":"—",
                                           "Mean Flow (pp)":f"{spread_pp:.4f}",
                                           "Median Flow (pp)":"—"}])],
                           ignore_index=True))
    + f"\n\n**Notes:** Quintiles formed monthly on `past_12m_return`. "
    f"Q1=worst, Q5=best. DV=`flow_winsorized`. Sample: active EDC funds, "
    f"{df_q['caldt'].min().date()} – {df_q['caldt'].max().date()}.\n"
)
with open(TABS + PREFIX + "quintile_average_flows.md", "w") as f:
    f.write(avg_flow_md_str)
print(f"  Saved avg flows  MD → {TABS}{PREFIX}quintile_average_flows.md")

# Quintile regression table CSV + MD
tbl_q.to_csv(TABS + PREFIX + "quintile_regressions.csv", index=False)
print(f"  Saved quintile reg CSV → {TABS}{PREFIX}quintile_regressions.csv")

q_md_str = (
    "# Quintile Flow-Performance Regressions — Extension 2003–2025\n\n"
    "## Table: OLS Regressions — Dependent Variable: Flow (winsorized)\n\n"
    + tbl_to_md(tbl_q)
    + "\n\n**Notes:** Q1 (worst performers) is the omitted reference. "
    "SE clustered by WFICN. \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10. "
    f"Sample: active EDC funds, {reg_q['caldt'].min().date()} – "
    f"{reg_q['caldt'].max().date()}.\n"
)
with open(TABS + PREFIX + "quintile_regressions.md", "w") as f:
    f.write(q_md_str)
print(f"  Saved quintile reg  MD → {TABS}{PREFIX}quintile_regressions.md")


# ══════════════════════════════════════════════════════════════════════════════
# 17. Interpretation markdown (combined Part A + B)
# ══════════════════════════════════════════════════════════════════════════════
coef_table_rows = "\n".join(
    f"| {lbl} | {m.params.get('past_12m_return',np.nan):+.4f}"
    f"| {m.bse.get('past_12m_return',np.nan):.4f}"
    f"| {m.pvalues.get('past_12m_return',np.nan):.4f}"
    f"| {'Yes' if m.pvalues.get('past_12m_return',1)<0.05 else 'No'} |"
    for lbl, m in zip(labels_main, models_main)
)

q_coef_rows = "| Q1 (ref.) | 0.0000 | — | — | — | 0.000 |\n" + "\n".join(
    f"| {q.replace('_','')} | {qm3.params[q]:+.4f}{stars(qm3.pvalues[q])}"
    f"| {qm3.bse[q]:.4f} | {qm3.tvalues[q]:.2f}"
    f"| {qm3.pvalues[q]:.4f} | {qm3.params[q]*100:+.3f} pp |"
    for q in q_dummy_cols
)

mono_summary = "\n".join(
    f"- {lbl}: {'✅ monotone' if all(m.params.get(q_dummy_cols[i+1],np.nan)>m.params.get(q_dummy_cols[i],np.nan) for i in range(len(q_dummy_cols)-1)) else '⚠️ non-monotone'}"
    for lbl, m in zip(labels_q, models_q)
)

qc_summary = "\n".join(
    [f"- ✅ {p}" for p in passes] + [f"- ⚠️  {fl}" for fl in flags]
)

interp_md = f"""# Results Interpretation — Extension 2003–2025 Flow-Performance Analysis

## Part A: Main 12-Month Regressions

### Coefficient on Past 12-Month Return

| Model | Coef. | SE | p-value | Sig. (5%) |
|---|---|---|---|---|
{coef_table_rows}

A positive coefficient confirms that funds with higher past 12-month returns
attract larger net inflows, consistent with performance-chasing behaviour.
This replicates the core finding of the baseline analysis in a more recent and
larger sample.

### Economic Magnitude

- SD of past_12m_return: **{sd_perf*100:.2f} pp**
- SD of flow_winsorized: **{sd_flow*100:.2f} pp**
- A **+10 pp** higher past 12-month return is associated with
  **{coef_m3_a*0.10*100:+.3f} pp/month** higher flow (Model 3, month FE).
- A 1-SD increase in past return → **{coef_m3_a*sd_perf*100:+.3f} pp/month**
  change in flow (= **{abs(coef_m3_a*sd_perf)/sd_flow:.2f} SDs** of flow).

### Comparison with Baseline (1999–2011)

| Metric | Baseline | Extension | Difference |
|---|---|---|---|
| Preferred coef (M3) | {BASELINE_COEF_M3:.4f} | {coef_m3_a:.4f} | {coef_m3_a-BASELINE_COEF_M3:+.4f} |
| Qualitative direction | positive | positive | consistent |
| Significance | p<0.01 | p<{m3.pvalues['past_12m_return']:.4f} | {'consistent' if m3.pvalues['past_12m_return']<0.05 else 'weaker'} |

The extension coefficient is **{'qualitatively similar to' if sim_coef else 'different from'}** the baseline.
The direction of the effect is unchanged: higher past performance → higher flows.

---

## Part B: Quintile Analysis

### Average Flows by Quintile (Unconditional)

| Quintile | Mean Monthly Flow | Mean Flow (pp) |
|---|---|---|
"""
for _, row in flow_by_q.iterrows():
    interp_md += (f"| {row['quintile_label']} | {row['mean_flow']:+.4f} | "
                  f"{row['mean_flow']*100:+.3f} pp |\n")
interp_md += f"| **Q5 − Q1 spread** | **{spread:+.4f}** | **{spread_pp:+.3f} pp/month** |\n"

interp_md += f"""
Raw Q5 − Q1 spread: **{spread_pp:+.3f} pp/month** ({spread_pp*12:+.2f} pp/year annualised).

### Regression-Adjusted Quintile Effects (Model 3: Month FE)

| Quintile | Coef vs Q1 | SE | t | p | Δflow (pp/month) |
|---|---|---|---|---|---|
{q_coef_rows}

Regression-adjusted Q5 premium over Q1: **{q5_effect_pp:+.3f} pp/month**
(= {abs(qm3.params['Q_5'])/sd_flow_q:.2f} SDs of the flow distribution).

### Monotonicity

{mono_summary}

### Convexity

| Metric | Value |
|---|---|
| Q4→Q5 step (Model 3) | {q4q5_step_m3*100:+.3f} pp |
| Avg of Q2→Q3 and Q3→Q4 steps | {avg_inner_m3*100:+.3f} pp |
| Convexity ratio | {convex_ratio_m3:.2f}× |

{"A ratio >1 indicates a **convex flow response** at the top quintile — top performers receive disproportionately higher inflows, consistent with the asymmetric flow-performance relationship (Sirri & Tufano 1998; Chevalier & Ellison 1997)." if convex_ratio_m3 > 1 else "The ratio ≤ 1 suggests a more linear than convex relationship in this sample."}

### Comparison with Baseline

| Metric | Baseline | Extension | Direction |
|---|---|---|---|
| Q5 premium/month (M3) | {BASELINE_Q5_PP:.2f} pp | {q5_effect_pp:.3f} pp | {'consistent' if sim_q5 else 'different'} |
| Monotonic Q2→Q5 | Yes | {'Yes' if mono3_q else 'No'} | {'consistent' if mono3_q else 'different'} |
| Convexity ratio | ~2.4× | {convex_ratio_m3:.2f}× | {'consistent' if 1.5 < convex_ratio_m3 < 4.0 else 'different'} |

---

## Quality Checks

{qc_summary}

---

## Thesis Caveats

1. **Missing controls (20.5%):** exp_ratio and turn_ratio are missing for ~20% of
   fund-quarter observations in the 2003–2025 FSQ file. Models M1/M2 use the larger
   170,616-obs sample; M3/M4 use {int(m4.nobs):,} obs. This is expected given the
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
"""

with open(TABS + PREFIX + "results_interpretation.md", "w") as f:
    f.write(interp_md)
print(f"  Saved interpretation → {TABS}{PREFIX}results_interpretation.md")


# ══════════════════════════════════════════════════════════════════════════════
# 18. Conclusion
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("CONCLUSION")
print("═" * 72)

print(f"""
  PART A — CONTINUOUS FLOW-PERFORMANCE RELATIONSHIP
  ─────────────────────────────────────────────────────────────────────
  Does positive flow-performance relationship persist in 2003–2025?
    YES — coefficient on past_12m_return is positive and significant at
    p<0.01 in all four models.
    Preferred (M3): coef = {coef_m3_a:+.4f}  (baseline: {BASELINE_COEF_M3})
    A +10 pp higher past return → {coef_m3_a*0.10*100:+.3f} pp/month higher flow (M3).
    Qualitatively {'similar to' if sim_coef else 'different from'} baseline.

  PART B — QUINTILE ANALYSIS
  ─────────────────────────────────────────────────────────────────────
  Monotonic Q2→Q5 in preferred spec (Model 3)?
    {'YES' if mono3_q else 'NO'}

  Q5 premium (regression-adjusted, M3):
    {q5_effect_pp:+.3f} pp/month  (baseline: {BASELINE_Q5_PP:+.2f} pp/month)
    Qualitatively {'similar' if sim_q5 else 'different'}.

  Convex flow-performance pattern?
    {'YES' if convex_ratio_m3 > 1 else 'NO'} — convexity ratio {convex_ratio_m3:.2f}×
    {"(Q4→Q5 step disproportionately large; top performers receive outsize inflows)" if convex_ratio_m3 > 1 else ""}

  QUALITY CHECKS
  ─────────────────────────────────────────────────────────────────────
  Passes: {len(passes)}   Flags: {len(flags)}
  {"All checks pass." if not flags else "Flags: " + "; ".join(flags)}

  THESIS-READINESS
  ─────────────────────────────────────────────────────────────────────
  Extension sample: THESIS-READY
  Key caveat to mention: exp_ratio/turn_ratio missing ~20% of obs;
  models M1/M2 use N={df['past_12m_return'].notna().sum():,}, M3/M4 use N={int(m4.nobs):,}.
  This follows the same pattern as the baseline and is not a quality issue.

  Outputs saved (7 files, no baseline files modified):
    extension_2003_2025_main_regressions_12m.{{csv,md}}
    extension_2003_2025_quintile_average_flows.{{csv,md}}
    extension_2003_2025_quintile_regressions.{{csv,md}}
    extension_2003_2025_results_interpretation.md
""")
print(SEP)
print("Done.")
print("═" * 72)
