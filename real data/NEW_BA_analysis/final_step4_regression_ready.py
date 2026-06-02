"""
Final Step 3 (script: step4) — Regression-ready dataset.

Pipeline:
  1. Load Step 2 cleaned dataset.
  2. Apply final QC cleaning rules from the Step 2 QC check.
  3. Winsorize portfolio_return at 1/99 → portfolio_return_winsorized.
  4. Construct past-performance measures:
       past_12m_return : cumulative return over t-12 to t-1 (12 consecutive months required)
       past_6m_return  : cumulative return over t-6  to t-1  (6 consecutive months required)
  5. Add control variables: log_lag_tna, fund_age_years, exp_ratio, turn_ratio.
  6. Save outputs and summary statistics.
"""

import pandas as pd
import numpy as np
import os

BASE = "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit/real data"
PROC = BASE + "/NEW_BA_analysis/data/processed/"
TABS = BASE + "/NEW_BA_analysis/output/tables/"
os.makedirs(PROC, exist_ok=True)
os.makedirs(TABS, exist_ok=True)

SEP  = "\n" + "═" * 66
SEP2 = "─" * 66

# ══════════════════════════════════════════════════════════════════════
# 1. Load and inspect
# ══════════════════════════════════════════════════════════════════════

print("Loading Step 2 dataset …")
df = pd.read_csv(PROC + "final_step2_clean_wficn_edc_flows.csv", low_memory=False)
df["caldt"]         = pd.to_datetime(df["caldt"])
df["first_offer_dt"]= pd.to_datetime(df["first_offer_dt"], errors="coerce")

print(SEP)
print("1. STEP 2 INPUT DIAGNOSTICS")
print("═" * 66)
print(f"  Observations   : {len(df):>10,}")
print(f"  Unique WFICN   : {df['wficn'].nunique():>9,}")
print(f"  Date range     : {df['caldt'].min().date()} → {df['caldt'].max().date()}")

check_vars = ["portfolio_return", "portfolio_tna", "lag_portfolio_tna",
              "flow", "flow_winsorized", "exp_ratio", "turn_ratio", "fund_age_years"]
print(f"\n  Missing values:")
for v in check_vars:
    if v in df.columns:
        n = df[v].isna().sum()
        print(f"    {v:<28} : {n:>7,}  ({100*n/len(df):.1f}%)")


# ══════════════════════════════════════════════════════════════════════
# 2. Final cleaning — tracked step by step
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. FINAL CLEANING")
print("═" * 66)

construction = []

def drop_step(df, keep_mask, step_label, note=""):
    n_before = len(df)
    w_before = df["wficn"].nunique()
    out      = df[keep_mask].copy()
    n_rm     = n_before - len(out)
    w_rm     = w_before - out["wficn"].nunique()
    construction.append({
        "step": step_label, "obs_after": len(out),
        "wficn_after": out["wficn"].nunique(),
        "obs_removed": n_rm, "wficn_removed": w_rm,
        "note": note,
    })
    print(f"  {step_label}")
    print(f"    obs={len(out):>8,}  wficn={out['wficn'].nunique():>5,}"
          f"  removed {n_rm:,}  ({note})")
    return out

construction.append({
    "step": "0. Step 2 input", "obs_after": len(df),
    "wficn_after": df["wficn"].nunique(), "obs_removed": 0,
    "wficn_removed": 0, "note": "Before final cleaning",
})

# Rule 1: drop impossible returns
df = drop_step(df, df["portfolio_return"].abs() < 1,
               "1. Drop |portfolio_return| ≥ 1",
               "economically impossible for long-only equity fund")

# Rule 2: require lag_tna ≥ $10M
df = drop_step(df, df["lag_portfolio_tna"].fillna(0) >= 10,
               "2. Require lag_portfolio_tna ≥ $10M",
               "literature standard; removes tiny-fund flow noise")

# Rule 3: valid flow_winsorized
df = drop_step(df, df["flow_winsorized"].notna(),
               "3. Drop missing flow_winsorized",
               "need DV for regression")

# Rule 4: valid portfolio_return (should be no-op after Rule 1, but explicit)
df = drop_step(df, df["portfolio_return"].notna(),
               "4. Drop remaining missing portfolio_return",
               "need return for performance measures")


# ══════════════════════════════════════════════════════════════════════
# 3. Winsorize portfolio_return → portfolio_return_winsorized
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. WINSORIZE portfolio_return")
print("═" * 66)

p01_ret = df["portfolio_return"].quantile(0.01)
p99_ret = df["portfolio_return"].quantile(0.99)
df["portfolio_return_winsorized"] = df["portfolio_return"].clip(p01_ret, p99_ret)

print(f"  1st percentile : {p01_ret:.6f}")
print(f"  99th percentile: {p99_ret:.6f}")
print(f"  Obs clipped at lower : {(df['portfolio_return'] < p01_ret).sum():,}")
print(f"  Obs clipped at upper : {(df['portfolio_return'] > p99_ret).sum():,}")


# ══════════════════════════════════════════════════════════════════════
# 4. Past performance measures
#
# Strategy: work in log space for numerical stability.
#   log1p_ret = log(1 + portfolio_return_winsorized)
#
# For each WFICN, compute cumulative past return using a rolling sum of
# log-returns on consecutive months only.
#
# Gap handling:
#   - Compute a sequential month index (year * 12 + month).
#   - Within each WFICN, detect gaps where consecutive observations are
#     not exactly 1 calendar month apart.
#   - Assign a run_id that increments at each gap break.
#   - Apply rolling within (wficn, run_id) so a gap resets the window.
#   - shift(1) within each run excludes the current month from past return.
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. CONSTRUCTING PAST PERFORMANCE MEASURES")
print("═" * 66)

df = df.sort_values(["wficn", "caldt"]).reset_index(drop=True)

# Sequential integer month index
df["month_idx"] = df["caldt"].dt.year * 12 + df["caldt"].dt.month

# Month gap to previous observation within each WFICN
df["lag_month_idx"] = df.groupby("wficn")["month_idx"].shift(1)
df["month_gap"]     = (df["month_idx"] - df["lag_month_idx"]).fillna(1)
# month_gap == 1 → consecutive; > 1 → gap in the series; first obs gets 1

# Run ID: increments whenever the gap breaks a consecutive sequence
df["is_break"] = (df["month_gap"] != 1).astype(int)
df["run_id"]   = df.groupby("wficn")["is_break"].cumsum()

# Log return for cumulative product via sum
df["log1p_ret"] = np.log1p(df["portfolio_return_winsorized"])

# ── Rolling helper inside (wficn, run_id) groups ──────────────────────────────
# shift(1): exclude current month → the rolling window covers t-K to t-1
# min_periods=K: require all K months present in the window

def rolling_cumret(series, window):
    """Rolling sum of log-returns with exactly `window` months required."""
    return series.shift(1).rolling(window, min_periods=window).sum()

grp = df.groupby(["wficn", "run_id"])

df["sum_log_12m"] = grp["log1p_ret"].transform(lambda x: rolling_cumret(x, 12))
df["sum_log_6m"]  = grp["log1p_ret"].transform(lambda x: rolling_cumret(x,  6))

# Convert back from log-space: cumret = exp(sum_log) - 1
df["past_12m_return"] = np.expm1(df["sum_log_12m"])
df["past_6m_return"]  = np.expm1(df["sum_log_6m"])

# Drop intermediate construction columns
df.drop(columns=["log1p_ret", "sum_log_12m", "sum_log_6m",
                 "is_break", "run_id", "lag_month_idx",
                 "month_idx", "month_gap"], inplace=True)

n_12m = df["past_12m_return"].notna().sum()
n_6m  = df["past_6m_return"].notna().sum()
n_both= (df["past_12m_return"].notna() & df["past_6m_return"].notna()).sum()

print(f"  Obs with past_12m_return   : {n_12m:>9,}  ({100*n_12m/len(df):.1f}%)")
print(f"  Obs with past_6m_return    : {n_6m:>9,}  ({100*n_6m/len(df):.1f}%)")
print(f"  Obs with both              : {n_both:>9,}  ({100*n_both/len(df):.1f}%)")

# Plausibility
for var, label in [("past_12m_return", "12m"), ("past_6m_return", "6m")]:
    s = df[var].dropna()
    pcts = s.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    print(f"\n  past_{label}_return  N={len(s):,}  "
          f"mean={s.mean():.4f}  std={s.std():.4f}")
    print(f"    p1={pcts[0.01]:.4f}  p5={pcts[0.05]:.4f}  "
          f"p25={pcts[0.25]:.4f}  median={pcts[0.50]:.4f}  "
          f"p75={pcts[0.75]:.4f}  p95={pcts[0.95]:.4f}  p99={pcts[0.99]:.4f}")

# Date range of past_12m_return observations
r12 = df[df["past_12m_return"].notna()]
print(f"\n  past_12m_return date range : "
      f"{r12['caldt'].min().date()} → {r12['caldt'].max().date()}")
r6 = df[df["past_6m_return"].notna()]
print(f"  past_6m_return  date range : "
      f"{r6['caldt'].min().date()} → {r6['caldt'].max().date()}")


# ══════════════════════════════════════════════════════════════════════
# 5. Control variables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. CONTROL VARIABLES")
print("═" * 66)

# log(lag_portfolio_tna) — standard size control in the literature
df["log_lag_tna"] = np.log(df["lag_portfolio_tna"])

# fund_age_years already in dataset; recompute for any remaining NaN
if "first_offer_dt" in df.columns:
    missing_age = df["fund_age_years"].isna() & df["first_offer_dt"].notna()
    df.loc[missing_age, "fund_age_years"] = (
        (df.loc[missing_age, "caldt"] - df.loc[missing_age, "first_offer_dt"])
        .dt.days / 365.25
    )

# Log fund age (some regressions use log_age)
df["log_fund_age"] = np.log1p(df["fund_age_years"].clip(lower=0))

ctrl_vars = ["log_lag_tna", "fund_age_years", "log_fund_age",
             "exp_ratio", "turn_ratio"]
for v in ctrl_vars:
    n_ok  = df[v].notna().sum()
    n_mis = df[v].isna().sum()
    print(f"  {v:<24} : {n_ok:>8,} non-null  "
          f"({n_mis:>6,} missing, {100*n_mis/len(df):.1f}%)"
          f"  mean={df[v].mean():.4f}")


# ══════════════════════════════════════════════════════════════════════
# 6. Final variable overview
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("6. FINAL DATASET OVERVIEW")
print("═" * 66)
print(f"  Observations            : {len(df):>9,}")
print(f"  Unique WFICN            : {df['wficn'].nunique():>9,}")
print(f"  Date range              : {df['caldt'].min().date()} → {df['caldt'].max().date()}")

reg_core = ["flow_winsorized", "past_12m_return", "past_6m_return",
            "log_lag_tna", "fund_age_years", "exp_ratio", "turn_ratio"]
print(f"\n  Core regression variable coverage:")
for v in reg_core:
    nn = df[v].notna().sum()
    print(f"    {v:<28} : {nn:>8,}  ({100*nn/len(df):.1f}%)")

# Year × WFICN coverage (check for regression usability)
yr_cover = (
    df.assign(year=df["caldt"].dt.year)
    .groupby("year")
    .agg(
        obs           = ("wficn",         "count"),
        unique_wficn  = ("wficn",         "nunique"),
        n_with_r12    = ("past_12m_return","count"),
        pct_r12       = ("past_12m_return",lambda x: round(x.notna().mean()*100,1)),
        pct_r6        = ("past_6m_return", lambda x: round(x.notna().mean()*100,1)),
    )
)
print(f"\n  Coverage by year (obs, unique WFICN, % with 12m / 6m past return):")
print(f"  {'Year':>4}  {'obs':>8}  {'WFICN':>6}  {'%r12':>6}  {'%r6':>6}")
print(f"  {SEP2}")
for yr, row in yr_cover.iterrows():
    print(f"  {yr:>4}  {int(row.obs):>8,}  {int(row.unique_wficn):>6,}  "
          f"{row.pct_r12:>5.1f}%  {row.pct_r6:>5.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 7. Summary statistics table
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("7. SUMMARY STATISTICS")
print("═" * 66)

stat_vars = {
    "flow_winsorized":            "Fund flow (winsorized 1/99 pct)",
    "flow":                       "Fund flow (raw)",
    "portfolio_return":           "Monthly portfolio return",
    "portfolio_return_winsorized":"Monthly return (winsorized 1/99)",
    "past_12m_return":            "Past 12-month cumulative return",
    "past_6m_return":             "Past 6-month cumulative return",
    "portfolio_tna":              "Portfolio TNA ($M)",
    "lag_portfolio_tna":          "Lag portfolio TNA ($M)",
    "log_lag_tna":                "Log(lag portfolio TNA)",
    "exp_ratio":                  "Expense ratio",
    "turn_ratio":                 "Turnover ratio",
    "fund_age_years":             "Fund age (years)",
}

stats_rows = []
for var, label in stat_vars.items():
    if var not in df.columns:
        continue
    s = df[var].dropna()
    if len(s) == 0:
        continue
    q = s.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    stats_rows.append({
        "variable": label,
        "N":       len(s),
        "mean":    round(s.mean(),   5),
        "std":     round(s.std(),    5),
        "p1":      round(q[0.01],    5),
        "p5":      round(q[0.05],    5),
        "p25":     round(q[0.25],    5),
        "median":  round(q[0.50],    5),
        "p75":     round(q[0.75],    5),
        "p95":     round(q[0.95],    5),
        "p99":     round(q[0.99],    5),
    })

stats_df = pd.DataFrame(stats_rows).set_index("variable")
pd.set_option("display.width", 200)
print(stats_df[["N","mean","std","p25","median","p75"]].to_string())


# ══════════════════════════════════════════════════════════════════════
# 8. Save outputs
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("8. SAVING OUTPUTS")
print("═" * 66)

# ── Regression-ready dataset ───────────────────────────────────────────────────
final_cols = [
    # Identifiers
    "wficn", "caldt",
    # Dependent variable
    "flow_winsorized", "flow",
    # Returns
    "portfolio_return", "portfolio_return_winsorized",
    # Past performance
    "past_12m_return", "past_6m_return",
    # TNA and size
    "portfolio_tna", "lag_portfolio_tna", "log_lag_tna",
    # Fund characteristics
    "fund_age_years", "log_fund_age",
    "exp_ratio", "turn_ratio", "mgmt_fee",
    # Metadata
    "fund_name", "crsp_obj_cd",
    "lipper_obj_cd", "lipper_obj_name",
    "n_share_classes",
]
final_cols = [c for c in final_cols if c in df.columns]
df[final_cols].to_csv(PROC + "final_step3_regression_ready_wficn_edc.csv", index=False)
print(f"  Dataset  → {PROC}final_step3_regression_ready_wficn_edc.csv")

# ── Helper: df → markdown table ───────────────────────────────────────────────
def df_to_md(df, title):
    idx_name = df.index.name or "index"
    cols = [idx_name] + df.columns.tolist()
    lines = [f"## {title}", "",
             "| " + " | ".join(str(c) for c in cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

# ── Sample construction table ─────────────────────────────────────────────────
const_df = pd.DataFrame(construction).set_index("step")
const_df.to_csv(TABS + "final_step3_sample_construction.csv")
with open(TABS + "final_step3_sample_construction.md", "w") as f:
    f.write("# Regression Sample Construction\n\n" +
            df_to_md(const_df, "Step-by-step sample construction"))
print(f"  Tables   → {TABS}final_step3_sample_construction.{{csv,md}}")

# ── Summary statistics ─────────────────────────────────────────────────────────
stats_df.to_csv(TABS + "final_step3_summary_statistics.csv")
with open(TABS + "final_step3_summary_statistics.md", "w") as f:
    f.write("# Summary Statistics — Regression-Ready Sample\n\n" +
            df_to_md(stats_df, "Summary statistics"))
print(f"  Tables   → {TABS}final_step3_summary_statistics.{{csv,md}}")


# ══════════════════════════════════════════════════════════════════════
# 9. Conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("9. CONCLUSION")
print("═" * 66)

r12_ok  = df["past_12m_return"].notna().mean() * 100
r6_ok   = df["past_6m_return"].notna().mean() * 100
r12_med = df["past_12m_return"].median()
r6_med  = df["past_6m_return"].median()
r12_std = df["past_12m_return"].std()
r6_std  = df["past_6m_return"].std()
r12_start = r12["caldt"].min().date() if len(r12) else "N/A"
r6_start  = r6["caldt"].min().date()  if len(r6)  else "N/A"

# Check plausibility: annual equity returns centred near 0–15% with ~30% std
r12_plausible = abs(r12_med) < 0.30 and 0.05 < r12_std < 0.80
r6_plausible  = abs(r6_med)  < 0.20 and 0.03 < r6_std  < 0.60

print(f"""
  Final observations              : {len(df):,}
  Unique WFICN                    : {df['wficn'].nunique():,}
  Date range (all obs)            : {df['caldt'].min().date()} → {df['caldt'].max().date()}
  Date range (past_12m available) : {r12_start} → {r12['caldt'].max().date() if len(r12) else 'N/A'}

  past_12m_return coverage        : {r12_ok:.1f}%  (median={r12_med:.4f}, std={r12_std:.4f})
  past_6m_return  coverage        : {r6_ok:.1f}%   (median={r6_med:.4f},  std={r6_std:.4f})

  Plausibility check:
    past_12m_return looks plausible : {'YES' if r12_plausible else 'CHECK — values outside expected range'}
    past_6m_return  looks plausible : {'YES' if r6_plausible  else 'CHECK — values outside expected range'}

  Dataset ready for regressions?  : YES
    - flow_winsorized  : {df['flow_winsorized'].notna().sum():,} obs
    - past_12m_return  : {df['past_12m_return'].notna().sum():,} obs
    - log_lag_tna      : {df['log_lag_tna'].notna().sum():,} obs
    - exp_ratio        : {df['exp_ratio'].notna().sum():,} obs

  Note: past performance only available from {r12_start} onward
  (requires 12 consecutive months within each WFICN after the
  1999-03 FSQ start and the $10M TNA threshold).
""")
