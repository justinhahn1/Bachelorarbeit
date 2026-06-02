"""
Final Step 2 — Merge Fund Summary, filter active EDC funds, calculate flows.

Pipeline:
  1. Load Step 1 WFICN-month dataset.
  2. Aggregate Fund Summary from crsp_fundno level to WFICN-quarter level.
  3. As-of merge (backward, no look-ahead) to attach fund characteristics to
     each WFICN-month.
  4. Apply sample filters step-by-step with full accounting.
  5. Calculate monthly fund flow and winsorize.
  6. Calculate fund age.
  7. Produce thesis-ready tables and quality checks.
  8. Save cleaned dataset and all diagnostic tables.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE = "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit/real data"
RAW  = BASE + "/real, clear data/raw/new data/"
PROC = BASE + "/NEW_BA_analysis/data/processed/"
TABS = BASE + "/NEW_BA_analysis/output/tables/"
os.makedirs(PROC, exist_ok=True)
os.makedirs(TABS, exist_ok=True)

SEP  = "\n" + "═" * 66
SEP2 = "─" * 66

# Keywords for name-based exclusions (applied to lower-cased text)
INDEX_TERMS = ["index", " idx ", "s&p 500", "s&p500", "russell", "wilshire",
               "msci", "dow jones", "nasdaq composite", "nasdaq-100",
               "stoxx", "ftse", " ixus"]
ETF_TERMS   = ["etf", "exchange traded fund", "exchange-traded fund", "etn "]
NONEQUITY_TERMS = [
    # International / foreign
    "international", "global", "world", "emerging market", "foreign",
    "overseas", "europe", "european", "pacific", "asia", "japan",
    "china", "india", "latin america",
    # Fixed income / bond
    "bond", "fixed income", "treasury", "government", "municipal",
    "corporate debt", "high yield", "credit", "income fund",
    # Money market
    "money market", "cash management", "liquid assets",
    # Balanced / allocation
    "balanced", "allocation", "flexible portfolio", "hybrid",
    # Real estate / sector
    "real estate", "reit", "sector fund",
    # Target date / lifecycle
    "target date", "target-date", "retirement fund", "lifecycle",
    # Commodity / other
    "commodity", "precious metal", "gold fund",
]


# ══════════════════════════════════════════════════════════════════════
# 1. Load files
# ══════════════════════════════════════════════════════════════════════

print("Loading files …")

step1 = pd.read_csv(PROC + "final_step1_wficn_portfolio_month.csv", low_memory=False)
fsq   = pd.read_csv(RAW  + "fund_summary_quarterly_1991_2011.csv",  low_memory=False)
mfl   = pd.read_csv(RAW  + "mflinks_crsp_fundno_wficn.csv",        low_memory=False)

# Normalise column names
for df in (step1, fsq, mfl):
    df.columns = df.columns.str.lower().str.strip()

step1["caldt"] = pd.to_datetime(step1["caldt"])
fsq["caldt"]   = pd.to_datetime(fsq["caldt"])

print(SEP)
print("1. STEP 1 DIAGNOSTICS")
print("═" * 66)
print(f"  Rows            : {len(step1):>10,}")
print(f"  Unique WFICN    : {step1['wficn'].nunique():>9,}")
print(f"  Date range      : {step1['caldt'].min().date()} → {step1['caldt'].max().date()}")
print(f"  Missing tna     : {step1['portfolio_tna'].isna().sum():>9,}")
print(f"  Missing return  : {step1['portfolio_return'].isna().sum():>9,}")


# ══════════════════════════════════════════════════════════════════════
# 2. Aggregate Fund Summary to WFICN × quarter level
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. AGGREGATING FUND SUMMARY TO WFICN-QUARTER LEVEL")
print("═" * 66)

# Map crsp_fundno → WFICN (canonical: modal WFICN per fundno)
wficn_map = (
    mfl.groupby("crsp_fundno")["wficn"]
    .agg(lambda x: x.mode().iloc[0])
    .reset_index()
)

# Attach WFICN to each FSQ row; drop fundnos not in MFLinks
fsq_w = fsq.merge(wficn_map, on="crsp_fundno", how="inner")
fsq_w["tna_latest"] = pd.to_numeric(fsq_w["tna_latest"], errors="coerce")
fsq_w["first_offer_dt"] = pd.to_datetime(fsq_w["first_offer_dt"], errors="coerce")

numeric_char_cols = ["exp_ratio", "turn_ratio", "mgmt_fee", "actual_12b1"]
for c in numeric_char_cols:
    fsq_w[c] = pd.to_numeric(fsq_w[c], errors="coerce")

print(f"  FSQ rows with WFICN match: {len(fsq_w):,} / {len(fsq):,}")
print(f"  Unique WFICN in FSQ      : {fsq_w['wficn'].nunique():,}")

# ── 2a. Representative categorical / name variables ────────────────────────────
# For each WFICN-quarter, pick the share class with the largest tna_latest.
# This share class is the most representative of the portfolio.
cat_cols = ["fund_name", "ticker", "crsp_obj_cd", "lipper_asset_cd",
            "lipper_obj_cd", "lipper_obj_name", "lipper_class", "lipper_class_name",
            "policy", "delist_cd"]

fsq_rep = (
    fsq_w
    .sort_values(["wficn", "caldt", "tna_latest"],
                 ascending=[True, True, False], na_position="last")
    .drop_duplicates(subset=["wficn", "caldt"])
    [["wficn", "caldt"] + cat_cols]
)

# ── 2b. Conservative flags per WFICN-quarter ──────────────────────────────────
# Any share class with a non-null flag marks the whole portfolio.
# index_fund_flag non-null = index; et_flag non-null = ETF.
fsq_w["_idx"] = fsq_w["index_fund_flag"].notna().astype(np.int8)
fsq_w["_etf"] = fsq_w["et_flag"].notna().astype(np.int8)
fsq_w["_ded"] = (fsq_w["dead_flag"].astype(str).str.upper() == "Y").astype(np.int8)

flag_agg = (
    fsq_w.groupby(["wficn", "caldt"])
    .agg(has_index_flag=("_idx", "max"),
         has_et_flag   =("_etf", "max"),
         dead_flag_any =("_ded", "max"))
    .reset_index()
)
flag_agg["has_index_flag"] = flag_agg["has_index_flag"].astype(bool)
flag_agg["has_et_flag"]    = flag_agg["has_et_flag"].astype(bool)
flag_agg["dead_flag_any"]  = flag_agg["dead_flag_any"].astype(bool)

# ── 2c. TNA-weighted mean of numeric characteristics per WFICN-quarter ─────────
# Use tna_latest as the weight; fall back to simple mean when tna is missing.
def tna_wavg_vectorized(df, val_col, grp_cols=["wficn", "caldt"]):
    valid = df[val_col].notna() & df["tna_latest"].notna() & (df["tna_latest"] > 0)
    df["_num"] = np.where(valid, df[val_col] * df["tna_latest"], np.nan)
    df["_den"] = np.where(valid, df["tna_latest"], np.nan)
    g = df.groupby(grp_cols)
    result = (g["_num"].sum(min_count=1) / g["_den"].sum(min_count=1)).reset_index()
    result.columns = grp_cols + [val_col]
    df.drop(columns=["_num", "_den"], inplace=True)
    return result

num_parts = [tna_wavg_vectorized(fsq_w.copy(), c) for c in numeric_char_cols]
num_agg = num_parts[0]
for part in num_parts[1:]:
    num_agg = num_agg.merge(part, on=["wficn", "caldt"], how="outer")

# ── 2d. Earliest first_offer_dt per WFICN (time-invariant) ────────────────────
first_offer = (
    fsq_w.groupby("wficn")["first_offer_dt"]
    .min()
    .reset_index()
    .rename(columns={"first_offer_dt": "first_offer_dt"})
)

# ── 2e. Combine all FSQ pieces ─────────────────────────────────────────────────
fsq_agg = (
    fsq_rep
    .merge(flag_agg, on=["wficn", "caldt"], how="left")
    .merge(num_agg,  on=["wficn", "caldt"], how="left")
    .merge(first_offer, on="wficn",         how="left")
)
print(f"  WFICN-quarter rows after aggregation: {len(fsq_agg):,}")
print(f"  Unique WFICN                        : {fsq_agg['wficn'].nunique():,}")
print(f"  Date range in FSQ-WFICN             : "
      f"{fsq_agg['caldt'].min().date()} → {fsq_agg['caldt'].max().date()}")


# ══════════════════════════════════════════════════════════════════════
# 3. As-of merge: WFICN-monthly ← WFICN-quarterly FSQ
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. AS-OF MERGE (Step 1 monthly ← FSQ quarterly, no look-ahead)")
print("═" * 66)

# merge_asof requires both frames sorted by the `on` column globally.
# direction='backward': for each monthly obs, attach the most recent quarterly
# FSQ entry with caldt <= monthly caldt. No tolerance — always use the latest
# available FSQ snapshot even if it is many quarters old (fund classification
# codes change rarely; this maximises coverage for pre-1999 data).
step1_s = step1.sort_values("caldt").reset_index(drop=True)
fsq_s   = fsq_agg.sort_values("caldt").reset_index(drop=True)

merged = pd.merge_asof(
    step1_s,
    fsq_s.rename(columns={"caldt": "fsq_caldt"}),
    left_on="caldt",
    right_on="fsq_caldt",
    by="wficn",
    direction="backward",
)
# Restore natural sort
merged = merged.sort_values(["wficn", "caldt"]).reset_index(drop=True)

n_with_fsq = merged["crsp_obj_cd"].notna().sum()
print(f"  WFICN-month rows                    : {len(merged):>10,}")
print(f"  Rows with FSQ characteristics       : {n_with_fsq:>10,}  "
      f"({100*n_with_fsq/len(merged):.1f}%)")
print(f"  Rows without FSQ (no match)         : {merged['crsp_obj_cd'].isna().sum():>10,}")


# ══════════════════════════════════════════════════════════════════════
# 4. Sample filters — tracked step by step
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. SAMPLE FILTERS")
print("═" * 66)

construction = []   # sample construction table rows
excl_detail  = []   # exclusion detail rows

def snap(df, step, note=""):
    construction.append({
        "step": step,
        "obs": len(df),
        "unique_wficn": df["wficn"].nunique(),
        "note": note,
    })
    return df

def drop_step(df, mask, step, note=""):
    """Apply boolean keep-mask, record stats, return filtered df."""
    n_before = len(df)
    w_before = df["wficn"].nunique()
    df_out   = df[mask].copy()
    n_removed = n_before - len(df_out)
    w_removed = w_before - df_out["wficn"].nunique()
    construction.append({
        "step": step,
        "obs": len(df_out),
        "unique_wficn": df_out["wficn"].nunique(),
        "obs_removed": n_removed,
        "wficn_removed": w_removed,
        "note": note,
    })
    return df_out

df = merged.copy()
snap(df, "0. All WFICN-month observations after merge")

# ── 4a. Valid TNA ──────────────────────────────────────────────────────────────
df = drop_step(df, df["portfolio_tna"].notna() & (df["portfolio_tna"] > 0),
               "1. Drop missing/zero portfolio_tna",
               "Requires positive TNA to compute flows")

# ── 4b. Valid return ───────────────────────────────────────────────────────────
df = drop_step(df, df["portfolio_return"].notna(),
               "2. Drop missing portfolio_return",
               "No return available for WFICN-month")

# ── 4c. Sample period filter ───────────────────────────────────────────────────
SAMPLE_START = pd.Timestamp("1997-07-01")
SAMPLE_END   = pd.Timestamp("2011-12-31")
df = drop_step(df, df["caldt"].between(SAMPLE_START, SAMPLE_END),
               "3. Keep 1997-07 to 2011-12",
               "Guide-paper sample window")

# ── 4d. EDC filter ────────────────────────────────────────────────────────────
# Primary filter: crsp_obj_cd starts with "EDC"
n_ed = (df["crsp_obj_cd"].str.startswith("ED", na=False)).sum()
edc_mask = df["crsp_obj_cd"].str.startswith("EDC", na=False)
df = drop_step(df, edc_mask,
               "4. Keep EDC funds (crsp_obj_cd starts with 'EDC')",
               f"Also note: 'ED' prefix would keep {n_ed:,} obs (see quality check)")

# ── 4e. Exclude ETFs ──────────────────────────────────────────────────────────
# Flag-based
etf_by_flag  = df["has_et_flag"].fillna(False)
# Name-based: check fund_name and lipper_obj_name
combined_txt = (
    df["fund_name"].fillna("").str.lower() + " " +
    df["lipper_obj_name"].fillna("").str.lower()
)
etf_by_name  = combined_txt.apply(lambda t: any(k in t for k in ETF_TERMS))

n_etf_flag  = etf_by_flag.sum()
n_etf_name  = (~etf_by_flag & etf_by_name).sum()
excl_detail.append({"exclusion": "ETF — et_flag",       "obs_removed": n_etf_flag})
excl_detail.append({"exclusion": "ETF — name-based",    "obs_removed": n_etf_name})

df = drop_step(df, ~(etf_by_flag | etf_by_name),
               "5. Exclude ETFs (flag + name)",
               f"Flag: {n_etf_flag:,}  Name: {n_etf_name:,}")

# ── 4f. Exclude index funds ───────────────────────────────────────────────────
idx_by_flag = df["has_index_flag"].fillna(False)
combined_txt2 = (
    df["fund_name"].fillna("").str.lower() + " " +
    df["lipper_obj_name"].fillna("").str.lower()
)
idx_by_name  = combined_txt2.apply(lambda t: any(k in t for k in INDEX_TERMS))

n_idx_flag  = idx_by_flag.sum()
n_idx_name  = (~idx_by_flag & idx_by_name).sum()
excl_detail.append({"exclusion": "Index — index_fund_flag", "obs_removed": n_idx_flag})
excl_detail.append({"exclusion": "Index — name-based",      "obs_removed": n_idx_name})

df = drop_step(df, ~(idx_by_flag | idx_by_name),
               "6. Exclude index funds (flag + name)",
               f"Flag: {n_idx_flag:,}  Name: {n_idx_name:,}")

# ── 4g. Exclude non-target fund types (safety net after EDC filter) ────────────
# Build a combined classification text from multiple columns
classif_txt = (
    df["fund_name"].fillna("").str.lower()          + " " +
    df["lipper_obj_name"].fillna("").str.lower()    + " " +
    df["lipper_class_name"].fillna("").str.lower()  + " " +
    df["policy"].fillna("").str.lower()
)
nontarget_mask = classif_txt.apply(lambda t: any(k in t for k in NONEQUITY_TERMS))
n_nontarget    = nontarget_mask.sum()
excl_detail.append({"exclusion": "Non-target type — name/classification",
                    "obs_removed": n_nontarget})

df = drop_step(df, ~nontarget_mask,
               "7. Exclude non-target types (international/bond/MM/balanced …)",
               f"{n_nontarget:,} obs caught by name/classification keywords")

snap(df, "8. Final cleaned sample")
print()
for row in construction:
    obs_rm  = row.get("obs_removed", "")
    obs_rm_str = f"  (removed {obs_rm:,})" if isinstance(obs_rm, int) else ""
    print(f"  Step {row['step']}")
    print(f"    obs={row['obs']:>9,}  wficn={row['unique_wficn']:>6,}{obs_rm_str}")
    if row.get("note"):
        print(f"    note: {row['note']}")


# ══════════════════════════════════════════════════════════════════════
# 5. Fund flow calculation
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. FLOW CALCULATION")
print("═" * 66)

# Sort within each WFICN and lag portfolio_tna by exactly one calendar month.
# We verify the gap is ≤ 35 days to guard against carrying a stale TNA
# across a multi-month observation gap.
df = df.sort_values(["wficn", "caldt"]).reset_index(drop=True)

df["lag_portfolio_tna"]  = df.groupby("wficn")["portfolio_tna"].shift(1)
df["lag_caldt"]          = df.groupby("wficn")["caldt"].shift(1)
df["caldt_gap_days"]     = (df["caldt"] - df["lag_caldt"]).dt.days

# Only use lag if gap is a plausible single-month window (28–35 days)
valid_lag = (
    df["lag_portfolio_tna"].notna() &
    (df["lag_portfolio_tna"] > 0) &
    (df["portfolio_tna"] > 0) &
    df["caldt_gap_days"].between(28, 35)
)

# Standard net-flow formula: flow = TNA_t / TNA_{t-1} - (1 + R_t)
df["flow"] = np.where(
    valid_lag,
    df["portfolio_tna"] / df["lag_portfolio_tna"] - (1 + df["portfolio_return"]),
    np.nan
)

n_flow = df["flow"].notna().sum()
print(f"  WFICN-months with valid flow   : {n_flow:>10,}  "
      f"({100*n_flow/len(df):.1f}%)")
print(f"  Missing flow (no valid lag TNA): {df['flow'].isna().sum():>10,}")

# Winsorize at 1st and 99th percentiles on the final sample
p01 = df["flow"].quantile(0.01)
p99 = df["flow"].quantile(0.99)
df["flow_winsorized"] = df["flow"].clip(lower=p01, upper=p99)
print(f"  Flow winsorization bounds      : [{p01:.4f}, {p99:.4f}]")
print(f"  Raw flow range                 : "
      f"[{df['flow'].min():.4f}, {df['flow'].max():.4f}]")


# ══════════════════════════════════════════════════════════════════════
# 6. Fund age
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("6. FUND AGE")
print("═" * 66)

df["fund_age_years"] = np.where(
    df["first_offer_dt"].notna(),
    (df["caldt"] - df["first_offer_dt"]).dt.days / 365.25,
    np.nan
)
n_age = df["fund_age_years"].notna().sum()
print(f"  Obs with valid fund age: {n_age:>9,}  ({100*n_age/len(df):.1f}%)")
print(f"  Age range              : "
      f"{df['fund_age_years'].min():.1f} → {df['fund_age_years'].max():.1f} years")


# ══════════════════════════════════════════════════════════════════════
# 7. Diagnostic / thesis-ready tables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("7. SUMMARY STATISTICS")
print("═" * 66)

stat_vars = {
    "flow":             "Raw fund flow",
    "flow_winsorized":  "Fund flow (winsorized 1/99)",
    "portfolio_return": "Monthly portfolio return",
    "portfolio_tna":    "Portfolio TNA ($M)",
    "lag_portfolio_tna":"Lag portfolio TNA ($M)",
    "exp_ratio":        "Expense ratio",
    "turn_ratio":       "Turnover ratio",
    "fund_age_years":   "Fund age (years)",
}

stats_rows = []
for var, label in stat_vars.items():
    s = df[var].dropna()
    if len(s) == 0:
        continue
    stats_rows.append({
        "variable": label,
        "N": len(s),
        "mean": round(s.mean(), 5),
        "std":  round(s.std(),  5),
        "p25":  round(s.quantile(0.25), 5),
        "median": round(s.median(), 5),
        "p75":  round(s.quantile(0.75), 5),
        "min":  round(s.min(), 5),
        "max":  round(s.max(), 5),
    })

stats_df = pd.DataFrame(stats_rows).set_index("variable")
print(stats_df[["N","mean","std","p25","median","p75"]].to_string())


# ══════════════════════════════════════════════════════════════════════
# 8. Quality checks
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("8. QUALITY CHECKS")
print("═" * 66)

qc_lines = ["# Final Step 2 — Quality Checks\n"]

# ── 8a. Top 20 WFICN-months by share-class count ─────────────────────────────
print("\n  a) Top 20 WFICN-months by n_share_classes:")
top_sc = (df.nlargest(20, "n_share_classes")
           [["wficn","caldt","n_share_classes","fund_name","portfolio_tna"]]
           .to_string(index=False))
print(top_sc)
qc_lines.append("## a) Top 20 WFICN-months by share-class count\n```\n"
                + top_sc + "\n```\n")

# ── 8b. Top 20 extreme raw flows ──────────────────────────────────────────────
print("\n  b) Top 20 absolute raw flow observations (before winsorization):")
top_flow = (df.assign(abs_flow=df["flow"].abs())
             .nlargest(20, "abs_flow")
             [["wficn","caldt","flow","portfolio_tna","lag_portfolio_tna","fund_name"]]
             .to_string(index=False))
print(top_flow)
qc_lines.append("## b) Top 20 absolute raw flow values\n```\n"
                + top_flow + "\n```\n")

# ── 8c. ETF / index name check in final sample ────────────────────────────────
print("\n  c) ETF/index keyword check in final sample:")
final_names = (
    df["fund_name"].fillna("").str.lower() + " " +
    df["lipper_obj_name"].fillna("").str.lower()
)
residual_etf   = final_names.apply(lambda t: any(k in t for k in ETF_TERMS))
residual_index = final_names.apply(lambda t: any(k in t for k in INDEX_TERMS))
print(f"    Obs with ETF term remaining   : {residual_etf.sum()}")
print(f"    Obs with index term remaining : {residual_index.sum()}")
if residual_index.any():
    print(df[residual_index][["wficn","fund_name","crsp_obj_cd"]].drop_duplicates("wficn").head(10).to_string(index=False))
qc_lines.append(f"## c) ETF/index residuals in final sample\n"
                f"- ETF terms remaining: {residual_etf.sum()}\n"
                f"- Index terms remaining: {residual_index.sum()}\n")

# ── 8d. crsp_obj_cd distribution in final sample ─────────────────────────────
print("\n  d) crsp_obj_cd distribution in final sample:")
obj_dist = df["crsp_obj_cd"].value_counts(dropna=False)
print(obj_dist.to_string())
qc_lines.append("## d) crsp_obj_cd distribution in final sample\n```\n"
                + obj_dist.to_string() + "\n```\n")

# Also report what would be in the "ED" (broader) sample for comparison
n_edc_strict = (df["crsp_obj_cd"].str.startswith("EDC", na=False)).sum()
n_ed_broader = (df["crsp_obj_cd"].str.startswith("ED",  na=False)).sum()
print(f"\n  [NOTE] 'EDC' prefix obs in final: {n_edc_strict:,} | "
      f"'ED' prefix obs: {n_ed_broader:,} "
      f"({'same' if n_edc_strict == n_ed_broader else 'DIFFERENT — some ED-non-EDC rows present'})")

# ── 8e. Date coverage by year in final sample ─────────────────────────────────
print("\n  e) Final sample — obs and unique WFICN by year:")
yr_cover = (
    df.assign(year=df["caldt"].dt.year)
    .groupby("year")
    .agg(obs=("wficn","count"), unique_wficn=("wficn","nunique"),
         pct_with_flow=("flow", lambda x: x.notna().mean() * 100))
    .round({"pct_with_flow": 1})
)
print(yr_cover.to_string())
qc_lines.append("## e) Date coverage by year in final sample\n```\n"
                + yr_cover.to_string() + "\n```\n")

# ── 8f. Lipper obj distribution ───────────────────────────────────────────────
print("\n  f) Top lipper_obj_name in final sample:")
lipper_dist = df["lipper_obj_name"].value_counts(dropna=False).head(20)
print(lipper_dist.to_string())
qc_lines.append("## f) Top 20 lipper_obj_name in final sample\n```\n"
                + lipper_dist.to_string() + "\n```\n")

# Write quality-check markdown
with open(TABS + "final_step2_quality_checks.md", "w") as f:
    f.write("\n".join(qc_lines))


# ══════════════════════════════════════════════════════════════════════
# 9. Save outputs
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("9. SAVING OUTPUTS")
print("═" * 66)

# ── Cleaned dataset ────────────────────────────────────────────────────────────
out_cols = [
    "wficn", "caldt",
    "portfolio_tna", "lag_portfolio_tna", "portfolio_return",
    "flow", "flow_winsorized",
    "n_share_classes", "n_valid_share_classes_for_return",
    "fund_name", "ticker", "crsp_obj_cd",
    "lipper_asset_cd", "lipper_obj_cd", "lipper_obj_name",
    "lipper_class", "lipper_class_name", "policy",
    "has_index_flag", "has_et_flag", "dead_flag_any",
    "exp_ratio", "turn_ratio", "mgmt_fee", "actual_12b1",
    "first_offer_dt", "fund_age_years",
    "fsq_caldt", "caldt_gap_days",
]
out_cols = [c for c in out_cols if c in df.columns]
df[out_cols].to_csv(PROC + "final_step2_clean_wficn_edc_flows.csv", index=False)
print(f"  Saved dataset → {PROC}final_step2_clean_wficn_edc_flows.csv")

# ── Helper: DataFrame → Markdown table ───────────────────────────────────────
def df_to_md(df, title):
    idx_name = df.index.name or "index"
    cols     = [idx_name] + df.columns.tolist()
    lines    = [f"## {title}", "",
                "| " + " | ".join(str(c) for c in cols) + " |",
                "| " + " | ".join(["---"] * len(cols)) + " |"]
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

# ── Sample construction table ─────────────────────────────────────────────────
const_df = pd.DataFrame(construction).fillna("").set_index("step")
const_df.to_csv(TABS + "final_step2_sample_construction.csv")
with open(TABS + "final_step2_sample_construction.md", "w") as f:
    f.write("# Sample Construction\n\n" + df_to_md(const_df, "Sample construction steps"))
print(f"  Saved → {TABS}final_step2_sample_construction.{{csv,md}}")

# ── Exclusion detail table ─────────────────────────────────────────────────────
excl_df = pd.DataFrame(excl_detail).set_index("exclusion")
excl_df.to_csv(TABS + "final_step2_exclusions.csv")
with open(TABS + "final_step2_exclusions.md", "w") as f:
    f.write("# Exclusion Detail\n\n" + df_to_md(excl_df, "Exclusion detail by criterion"))
print(f"  Saved → {TABS}final_step2_exclusions.{{csv,md}}")

# ── Summary statistics table ──────────────────────────────────────────────────
stats_df.to_csv(TABS + "final_step2_summary_statistics.csv")
with open(TABS + "final_step2_summary_statistics.md", "w") as f:
    f.write("# Summary Statistics\n\n" +
            df_to_md(stats_df[["N","mean","std","p25","median","p75","min","max"]],
                     "Summary statistics — final cleaned sample"))
print(f"  Saved → {TABS}final_step2_summary_statistics.{{csv,md}}")


# ══════════════════════════════════════════════════════════════════════
# 10. Conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("10. CONCLUSION")
print("═" * 66)

n_final     = len(df)
w_final     = df["wficn"].nunique()
date_min    = df["caldt"].min().date()
date_max    = df["caldt"].max().date()
pct_flow    = df["flow"].notna().mean() * 100
flow_med    = df["flow_winsorized"].median()
flow_p99    = df["flow"].quantile(0.99)
flow_p01    = df["flow"].quantile(0.01)
all_edc     = df["crsp_obj_cd"].str.startswith("EDC", na=False).all()
no_etf_flag = (~df["has_et_flag"].fillna(False)).all()
no_idx_flag = (~df["has_index_flag"].fillna(False)).all()

print(f"""
  Final observations          : {n_final:>10,}
  Unique WFICN                : {w_final:>10,}
  Date range                  : {date_min} → {date_max}
  Obs with valid flow         : {pct_flow:.1f}%

  EDC filter worked?          : {"YES — all crsp_obj_cd start with 'EDC'" if all_edc else "PARTIAL — check obj_cd dist"}
  ETF flag exclusion worked?  : {"YES — no et_flag in sample" if no_etf_flag else "PARTIAL — some et_flag remain"}
  Index flag exclusion worked?: {"YES — no index_fund_flag in sample" if no_idx_flag else "PARTIAL — some index flags remain"}

  Flow plausibility:
    Winsorization bounds      : [{p01:.4f}, {p99:.4f}]
    Median winsorized flow    : {flow_med:.4f}  {"(plausible, near zero)" if abs(flow_med) < 0.05 else "(check — may be large)"}
    Flow range after winsor.  : [{df['flow_winsorized'].min():.4f}, {df['flow_winsorized'].max():.4f}]

  1997–2011 sample usable?
    Year range covered        : {date_min.year} – {date_max.year}
    Unique WFICN in 1997      : {df[df['caldt'].dt.year==1997]['wficn'].nunique():,}
    Unique WFICN in 2011      : {df[df['caldt'].dt.year==2011]['wficn'].nunique():,}
    Flow coverage 1997–1999   : {df[df['caldt'].dt.year<=1999]['flow'].notna().mean()*100:.1f}%
    Flow coverage 2000–2011   : {df[df['caldt'].dt.year>=2000]['flow'].notna().mean()*100:.1f}%
""")
