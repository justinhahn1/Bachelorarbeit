"""
Final Step 5 — Main flow-performance regressions
DV : flow_winsorized
IV : past_12m_return (lagged, gap-aware 12-month cumulative return)

Models
  1. Baseline   : flow ~ past_12m_return
  2. Controls   : Model 1 + log_lag_tna + exp_ratio + fund_age_years + turn_ratio
  3. Month FE   : Model 2 + month dummies (caldt period, drop first)
  4. Month+EDC  : Model 3 + crsp_obj_cd dummies (EDCS baseline; EDCM, EDCI)

Standard errors : clustered on wficn throughout (statsmodels cov_type='cluster')
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

SEP  = "\n" + "═" * 72
SEP2 = "─" * 72

# ══════════════════════════════════════════════════════════════════════════════
# 1. Load regression-ready dataset
# ══════════════════════════════════════════════════════════════════════════════
print("Loading regression-ready dataset …")
df = pd.read_csv(PROC + "final_step3_regression_ready_wficn_edc.csv",
                 low_memory=False)
df["caldt"] = pd.to_datetime(df["caldt"])

print(f"  Rows loaded          : {len(df):>10,}")
print(f"  Unique WFICN         : {df['wficn'].nunique():>10,}")
print(f"  Date range           : {df['caldt'].min().date()} → {df['caldt'].max().date()}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Build regression sample
# ══════════════════════════════════════════════════════════════════════════════
controls = ["log_lag_tna", "exp_ratio", "fund_age_years", "turn_ratio"]
required = ["flow_winsorized", "past_12m_return"] + controls

reg = df.dropna(subset=required).copy()
print(SEP)
print("2. REGRESSION SAMPLE")
print("═" * 72)
print(f"\n  Obs after dropping NaN in required vars : {len(reg):>9,}")
print(f"  Unique WFICN                            : {reg['wficn'].nunique():>9,}")
print(f"  Date range                              : "
      f"{reg['caldt'].min().date()} → {reg['caldt'].max().date()}")
print(f"  Unique months                           : {reg['caldt'].nunique():>9,}")

# crsp_obj_cd distribution
print(f"\n  crsp_obj_cd counts:")
for code, cnt in reg["crsp_obj_cd"].value_counts().items():
    print(f"    {code:>6} : {cnt:>9,}  ({100*cnt/len(reg):.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Construct regressors
# ══════════════════════════════════════════════════════════════════════════════

# Month dummies (period string → dummy; EDCS is baseline for EDC dummies)
reg["month_str"] = reg["caldt"].dt.to_period("M").astype(str)
month_dummies = pd.get_dummies(reg["month_str"], prefix="m", drop_first=True,
                               dtype=float)

# EDC style dummies (EDCS = baseline)
edc_dummies = pd.get_dummies(reg["crsp_obj_cd"], prefix="edc", drop_first=False,
                             dtype=float)
# keep EDCM and EDCI only (EDCS is baseline; if EDCL present, include it)
edc_cols = [c for c in edc_dummies.columns if c != "edc_EDCS"]
edc_dummies = edc_dummies[edc_cols]

# Reset index for clean concat
reg = reg.reset_index(drop=True)
month_dummies = month_dummies.reset_index(drop=True)
edc_dummies   = edc_dummies.reset_index(drop=True)

Y = reg["flow_winsorized"]
X_base = sm.add_constant(reg["past_12m_return"])
X_ctrl = sm.add_constant(reg[["past_12m_return"] + controls])
X_mfe  = sm.add_constant(pd.concat([reg[["past_12m_return"] + controls],
                                     month_dummies], axis=1))
X_both = sm.add_constant(pd.concat([reg[["past_12m_return"] + controls],
                                     month_dummies, edc_dummies], axis=1))

cluster_ids = reg["wficn"].values

# ══════════════════════════════════════════════════════════════════════════════
# 4. Run regressions
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("4. RUNNING REGRESSIONS")
print("═" * 72)

def run_ols(Y, X, cluster_ids, label):
    model = sm.OLS(Y, X).fit(
        cov_type="cluster",
        cov_kwds={"groups": cluster_ids}
    )
    print(f"\n  {label}")
    print(f"    N={model.nobs:,.0f}  R²={model.rsquared:.4f}  "
          f"adj-R²={model.rsquared_adj:.4f}")
    return model

m1 = run_ols(Y, X_base, cluster_ids, "Model 1: Baseline")
m2 = run_ols(Y, X_ctrl, cluster_ids, "Model 2: Controls")
m3 = run_ols(Y, X_mfe,  cluster_ids, "Model 3: Controls + Month FE")
m4 = run_ols(Y, X_both, cluster_ids, "Model 4: Controls + Month FE + EDC FE")

models = [m1, m2, m3, m4]
labels = ["(1) Baseline", "(2) Controls", "(3) Month FE", "(4) Month+EDC FE"]

# ══════════════════════════════════════════════════════════════════════════════
# 5. Build thesis-ready table
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("5. REGRESSION TABLE")
print("═" * 72)

# Variables to display (excludes month/edc dummies)
display_vars = ["past_12m_return"] + controls + ["const"]
display_labels = {
    "past_12m_return" : "Past 12m Return",
    "log_lag_tna"     : "log(TNA_{t-1})",
    "exp_ratio"       : "Expense Ratio",
    "fund_age_years"  : "Fund Age (years)",
    "turn_ratio"      : "Turnover Ratio",
    "const"           : "Constant",
}

def stars(pval):
    if pval < 0.01:  return "***"
    if pval < 0.05:  return "**"
    if pval < 0.10:  return "*"
    return ""

rows = []
for var in display_vars:
    label = display_labels.get(var, var)
    coef_row  = {"Variable": label}
    se_row    = {"Variable": ""}
    for i, (m, lbl) in enumerate(zip(models, labels), 1):
        if var in m.params.index:
            c = m.params[var]
            s = m.bse[var]
            p = m.pvalues[var]
            coef_row[f"M{i}"] = f"{c:.4f}{stars(p)}"
            se_row[f"M{i}"]   = f"({s:.4f})"
        else:
            coef_row[f"M{i}"] = "—"
            se_row[f"M{i}"]   = ""
    rows.append(coef_row)
    rows.append(se_row)

# Footer
nobs_row  = {"Variable": "N"}
r2_row    = {"Variable": "R²"}
adjr2_row = {"Variable": "Adj. R²"}
mfe_row   = {"Variable": "Month FE"}
edcfe_row = {"Variable": "EDC Style FE"}
for i, m in enumerate(models, 1):
    nobs_row[f"M{i}"]  = f"{int(m.nobs):,}"
    r2_row[f"M{i}"]    = f"{m.rsquared:.4f}"
    adjr2_row[f"M{i}"] = f"{m.rsquared_adj:.4f}"
mfe_row["M1"]  = "No";  mfe_row["M2"]  = "No"
mfe_row["M3"]  = "Yes"; mfe_row["M4"]  = "Yes"
edcfe_row["M1"] = "No"; edcfe_row["M2"] = "No"
edcfe_row["M3"] = "No"; edcfe_row["M4"] = "Yes"

rows += [nobs_row, r2_row, adjr2_row, mfe_row, edcfe_row]

tbl = pd.DataFrame(rows, columns=["Variable", "M1", "M2", "M3", "M4"])
tbl.columns = ["Variable"] + labels

# Print to console
col_w = [28, 18, 18, 18, 18]
header = "  " + "  ".join(str(c).ljust(w) for c, w in zip(tbl.columns, col_w))
print(f"\n{header}")
print(f"  {SEP2}")
for _, row in tbl.iterrows():
    print("  " + "  ".join(str(v).ljust(w) for v, w in zip(row, col_w)))

print(f"\n  Notes: DV = flow_winsorized. Standard errors clustered by WFICN.")
print(f"         *** p<0.01  ** p<0.05  * p<0.10")
print(f"         Sample: active EDC WFICN-month obs, 1999-2011.")

# ══════════════════════════════════════════════════════════════════════════════
# 6. Save CSV
# ══════════════════════════════════════════════════════════════════════════════
tbl.to_csv(TABS + "final_step4_main_regressions_12m.csv", index=False)
print(f"\n  Saved CSV → {TABS}final_step4_main_regressions_12m.csv")

# ══════════════════════════════════════════════════════════════════════════════
# 7. Save Markdown
# ══════════════════════════════════════════════════════════════════════════════
def tbl_to_md(df):
    cols = df.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)

md = f"""# Flow-Performance Regressions — Active EDC Funds (WFICN, 1999–2011)

## Table: OLS Regressions — Dependent Variable: Flow (winsorized)

{tbl_to_md(tbl)}

**Notes:**
Standard errors clustered by WFICN.
\\*** p<0.01, \\** p<0.05, \\* p<0.10
Sample: active domestic equity (EDC) funds, 1999–2011.
Past 12m Return is the gap-aware cumulative 12-month lagged return (excludes current month).
"""

with open(TABS + "final_step4_main_regressions_12m.md", "w") as f:
    f.write(md)
print(f"  Saved  MD → {TABS}final_step4_main_regressions_12m.md")

# ══════════════════════════════════════════════════════════════════════════════
# 8. Economic interpretation
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("8. ECONOMIC INTERPRETATION")
print("═" * 72)

coef_m1 = m1.params["past_12m_return"]
se_m1   = m1.bse["past_12m_return"]
pv_m1   = m1.pvalues["past_12m_return"]
coef_m3 = m3.params["past_12m_return"]
se_m3   = m3.bse["past_12m_return"]
pv_m3   = m3.pvalues["past_12m_return"]
coef_m4 = m4.params["past_12m_return"]
se_m4   = m4.bse["past_12m_return"]
pv_m4   = m4.pvalues["past_12m_return"]

print(f"\n  past_12m_return coefficient:")
print(f"    Model 1 (baseline)   : {coef_m1:+.4f}  (SE={se_m1:.4f}, p={pv_m1:.4f}){stars(pv_m1)}")
print(f"    Model 3 (month FE)   : {coef_m3:+.4f}  (SE={se_m3:.4f}, p={pv_m3:.4f}){stars(pv_m3)}")
print(f"    Model 4 (month+EDC)  : {coef_m4:+.4f}  (SE={se_m4:.4f}, p={pv_m4:.4f}){stars(pv_m4)}")

# Economic magnitude: 1 SD past_12m_return → flow change
sd_perf = reg["past_12m_return"].std()
sd_flow = reg["flow_winsorized"].std()
print(f"\n  SD of past_12m_return  : {sd_perf:.4f}  ({sd_perf*100:.2f} pp)")
print(f"  SD of flow_winsorized  : {sd_flow:.4f}  ({sd_flow*100:.2f} pp)")
print(f"\n  1-SD increase in past_12m_return → flow change:")
for lbl, coef in [("Model 1", coef_m1), ("Model 3", coef_m3), ("Model 4", coef_m4)]:
    delta = coef * sd_perf
    print(f"    {lbl} : {delta:+.4f} ({delta*100:+.2f} pp)  "
          f"= {abs(delta)/sd_flow:.2f} SDs of flow")

# Significance summary
print(f"\n  Significance at 5% level:")
for lbl, m in zip(labels, models):
    pv = m.pvalues.get("past_12m_return", np.nan)
    sig = "YES" if pv < 0.05 else "NO "
    print(f"    {lbl:<22} : {sig}  (p={pv:.4f})")

# ── Save interpretation markdown ──────────────────────────────────────────────
interp_coef_table = "\n".join([
    f"| {lbl} | {m.params.get('past_12m_return', np.nan):+.4f} "
    f"| {m.bse.get('past_12m_return', np.nan):.4f} "
    f"| {m.pvalues.get('past_12m_return', np.nan):.4f} "
    f"| {'Yes' if 'past_12m_return' in m.params and m.pvalues.get('past_12m_return',1)<0.05 else 'No'} |"
    for lbl, m in zip(labels, models)
])

interp_md = f"""# Regression Interpretation — Flow-Performance, Active EDC Funds

## Main Finding

The coefficient on *Past 12m Return* measures the sensitivity of fund flows to
lagged 12-month performance.

| Model | Coef. | SE | p-value | Sig. (5%) |
|---|---|---|---|---|
{interp_coef_table}

**A positive coefficient** means that funds with higher past returns attract
more inflows (a flow-chasing / performance-chasing pattern), consistent with
the empirical literature (e.g., Sirri & Tufano 1998; Barber et al. 2022).

## Economic Magnitude

- Standard deviation of past_12m_return: **{sd_perf*100:.2f} pp**
- Standard deviation of flow_winsorized: **{sd_flow*100:.2f} pp**

A one-SD increase in past 12-month return is associated with a
**{coef_m3 * sd_perf * 100:+.2f} pp** change in monthly flow (Model 3, month FE),
equivalent to **{abs(coef_m3 * sd_perf)/sd_flow:.2f} standard deviations** of the flow distribution.

## Controls

- **log(TNA_{"{t-1}"})**:  larger funds attract proportionally smaller flows (scale effect).
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

- Period: {reg['caldt'].min().date()} to {reg['caldt'].max().date()}
- N (full model): {int(m4.nobs):,} WFICN-month observations
- Unique funds: {reg['wficn'].nunique():,} WFICNs
- Fund universe: active domestic equity (EDC) funds only
"""

with open(TABS + "final_step4_main_regression_interpretation.md", "w") as f:
    f.write(interp_md)
print(f"\n  Saved interpretation → {TABS}final_step4_main_regression_interpretation.md")

print(SEP)
print("Done.")
print("═" * 72)
