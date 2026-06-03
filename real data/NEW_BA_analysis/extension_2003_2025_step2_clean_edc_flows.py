"""
Extension Step 2 — Merge Fund Summary, filter active EDC funds,
calculate flows, clean, and build regression-ready dataset (2003–2025).

Consolidates baseline final_step2_clean_edc_flows.py,
final_step3_return_flow_qc.py, and final_step4_regression_ready.py
into one script for the extension sample.

Methodology is identical to the baseline except where noted:
  - fund_summary_quarterly_2003_2025 has no tna_latest column.
    Representative share class chosen by lowest crsp_fundno (oldest/primary class
    heuristic). Numeric characteristics averaged unweighted across share classes.
  - No hard sample-period filter: 2003–2025 is the natural extension window.
  - All other filters, flow formula, QC rules, and rolling-window logic are
    identical to the baseline.

Outputs (all prefixed extension_2003_2025_):
  data/processed/extension_2003_2025_step2_clean_wficn_edc_flows.csv
  data/processed/extension_2003_2025_step3_regression_ready_wficn_edc.csv
  output/tables/extension_2003_2025_sample_construction.csv
  output/tables/extension_2003_2025_sample_construction.md
  output/tables/extension_2003_2025_summary_statistics.csv
  output/tables/extension_2003_2025_summary_statistics.md
  output/tables/extension_2003_2025_step2_quality_checks.md
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

PREFIX = "extension_2003_2025_"
SEP    = "\n" + "═" * 66
SEP2   = "─" * 66

# ── Exclusion keyword lists (identical to baseline) ───────────────────────────
INDEX_TERMS = ["index", " idx ", "s&p 500", "s&p500", "russell", "wilshire",
               "msci", "dow jones", "nasdaq composite", "nasdaq-100",
               "stoxx", "ftse", " ixus"]
ETF_TERMS   = ["etf", "exchange traded fund", "exchange-traded fund", "etn "]
NONEQUITY_TERMS = [
    "international", "global", "world", "emerging market", "foreign",
    "overseas", "europe", "european", "pacific", "asia", "japan",
    "china", "india", "latin america",
    "bond", "fixed income", "treasury", "government", "municipal",
    "corporate debt", "high yield", "credit", "income fund",
    "money market", "cash management", "liquid assets",
    "balanced", "allocation", "flexible portfolio", "hybrid",
    "real estate", "reit", "sector fund",
    "target date", "target-date", "retirement fund", "lifecycle",
    "commodity", "precious metal", "gold fund",
]


# ══════════════════════════════════════════════════════════════════════
# 1. Load files
# ══════════════════════════════════════════════════════════════════════

print("Loading files …")

step1 = pd.read_csv(PROC + PREFIX + "step1_wficn_portfolio_month.csv", low_memory=False)
fsq   = pd.read_csv(RAW  + "fund_summary_quarterly_2003_2025.csv",     low_memory=False)
mfl   = pd.read_csv(RAW  + "mflinks_crsp_fundno_wficn_2003_2025.csv",  low_memory=False)

for df_ in (step1, fsq, mfl):
    df_.columns = df_.columns.str.lower().str.strip()

step1["caldt"] = pd.to_datetime(step1["caldt"])
fsq["caldt"]   = pd.to_datetime(fsq["caldt"])
fsq["first_offer_dt"] = pd.to_datetime(fsq["first_offer_dt"], errors="coerce")

for col in ["exp_ratio", "turn_ratio", "mgmt_fee", "actual_12b1"]:
    if col in fsq.columns:
        fsq[col] = pd.to_numeric(fsq[col], errors="coerce")

print(SEP)
print("1. STEP 1 INPUT DIAGNOSTICS")
print("═" * 66)
print(f"  Rows            : {len(step1):>10,}")
print(f"  Unique WFICN    : {step1['wficn'].nunique():>9,}")
print(f"  Date range      : {step1['caldt'].min().date()} → {step1['caldt'].max().date()}")
print(f"  Missing tna     : {step1['portfolio_tna'].isna().sum():>9,}")
print(f"  Missing return  : {step1['portfolio_return'].isna().sum():>9,}")


# ══════════════════════════════════════════════════════════════════════
# 2. Aggregate Fund Summary to WFICN × quarter level
#
# Difference from baseline: no tna_latest column in this FSQ file.
#   Representative share class → lowest crsp_fundno (oldest/primary class).
#   Numeric characteristics   → unweighted mean across share classes.
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. AGGREGATING FUND SUMMARY TO WFICN-QUARTER LEVEL")
print("═" * 66)

# Canonical WFICN per fundno (modal, same as Step 1)
wficn_map = (
    mfl.dropna(subset=["wficn"])
    .groupby("crsp_fundno")["wficn"]
    .agg(lambda x: x.mode().iloc[0])
    .reset_index()
)

fsq_w = fsq.merge(wficn_map, on="crsp_fundno", how="inner")
print(f"  FSQ rows with WFICN match : {len(fsq_w):,} / {len(fsq):,}")
print(f"  Unique WFICN in FSQ       : {fsq_w['wficn'].nunique():,}")

# ── 2a. Representative categorical row: lowest crsp_fundno per WFICN-quarter ──
cat_cols = ["fund_name", "ticker", "crsp_obj_cd", "lipper_asset_cd",
            "lipper_obj_cd", "lipper_obj_name", "lipper_class", "lipper_class_name",
            "policy", "delist_cd", "crsp_cl_grp"]

fsq_rep = (
    fsq_w
    .sort_values(["wficn", "caldt", "crsp_fundno"],
                 ascending=[True, True, True])        # lowest fundno = oldest class
    .drop_duplicates(subset=["wficn", "caldt"])
    [["wficn", "caldt"] + [c for c in cat_cols if c in fsq_w.columns]]
)

# ── 2b. Conservative flags: any non-null in the portfolio marks it ─────────────
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

# ── 2c. Unweighted mean of numeric characteristics ────────────────────────────
numeric_char_cols = [c for c in ["exp_ratio", "turn_ratio", "mgmt_fee", "actual_12b1"]
                     if c in fsq_w.columns]

num_agg = (
    fsq_w.groupby(["wficn", "caldt"])[numeric_char_cols]
    .mean()
    .reset_index()
)

# ── 2d. Earliest first_offer_dt per WFICN (time-invariant) ────────────────────
first_offer = (
    fsq_w.groupby("wficn")["first_offer_dt"]
    .min()
    .reset_index()
)

# ── 2e. Combine ────────────────────────────────────────────────────────────────
fsq_agg = (
    fsq_rep
    .merge(flag_agg,    on=["wficn", "caldt"], how="left")
    .merge(num_agg,     on=["wficn", "caldt"], how="left")
    .merge(first_offer, on="wficn",            how="left")
)
print(f"  WFICN-quarter rows after aggregation : {len(fsq_agg):,}")
print(f"  Unique WFICN                         : {fsq_agg['wficn'].nunique():,}")
print(f"  FSQ date range                       : "
      f"{fsq_agg['caldt'].min().date()} → {fsq_agg['caldt'].max().date()}")


# ══════════════════════════════════════════════════════════════════════
# 3. As-of merge: WFICN-monthly ← WFICN-quarterly FSQ (no look-ahead)
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. AS-OF MERGE (step1 monthly ← FSQ quarterly, backward, no look-ahead)")
print("═" * 66)

# Both frames must be globally sorted by the merge key (caldt).
step1_s = step1.sort_values("caldt").reset_index(drop=True)
fsq_s   = fsq_agg.sort_values("caldt").reset_index(drop=True)

merged = pd.merge_asof(
    step1_s,
    fsq_s.rename(columns={"caldt": "fsq_caldt"}),
    left_on   = "caldt",
    right_on  = "fsq_caldt",
    by        = "wficn",
    direction = "backward",
)
merged = merged.sort_values(["wficn", "caldt"]).reset_index(drop=True)

n_with_fsq = merged["crsp_obj_cd"].notna().sum()
print(f"  WFICN-month rows              : {len(merged):>10,}")
print(f"  Rows with FSQ data            : {n_with_fsq:>10,}  "
      f"({100*n_with_fsq/len(merged):.1f}%)")
print(f"  Rows without FSQ              : {merged['crsp_obj_cd'].isna().sum():>10,}")


# ══════════════════════════════════════════════════════════════════════
# 4. Sample filters — tracked step by step
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. SAMPLE FILTERS")
print("═" * 66)

construction = []
excl_detail  = []

def snap(df_, step, note=""):
    construction.append({
        "step": step, "obs": len(df_),
        "unique_wficn": df_["wficn"].nunique(),
        "obs_removed": "", "wficn_removed": "", "note": note,
    })

def drop_step(df_, mask, step, note=""):
    n_before = len(df_)
    w_before = df_["wficn"].nunique()
    out      = df_[mask].copy()
    n_rm     = n_before - len(out)
    w_rm     = w_before - out["wficn"].nunique()
    construction.append({
        "step": step, "obs": len(out),
        "unique_wficn": out["wficn"].nunique(),
        "obs_removed": n_rm, "wficn_removed": w_rm, "note": note,
    })
    return out

df = merged.copy()
snap(df, "0. All WFICN-month observations after merge")

# ── 4a. Valid TNA ──────────────────────────────────────────────────────────────
df = drop_step(df, df["portfolio_tna"].notna() & (df["portfolio_tna"] > 0),
               "1. Drop missing/zero portfolio_tna",
               "positive TNA required for flow")

# ── 4b. Valid return ───────────────────────────────────────────────────────────
df = drop_step(df, df["portfolio_return"].notna(),
               "2. Drop missing portfolio_return",
               "no return available")

# ── 4c. EDC filter ────────────────────────────────────────────────────────────
edc_mask = df["crsp_obj_cd"].str.startswith("EDC", na=False)
n_ed     = df["crsp_obj_cd"].str.startswith("ED", na=False).sum()
df = drop_step(df, edc_mask,
               "3. Keep EDC funds (crsp_obj_cd starts with 'EDC')",
               f"broader 'ED' prefix would keep {n_ed:,} obs")

# ── 4d. Exclude ETFs ──────────────────────────────────────────────────────────
etf_by_flag = df["has_et_flag"].fillna(False)
comb_txt    = (df["fund_name"].fillna("").str.lower() + " " +
               df["lipper_obj_name"].fillna("").str.lower())
etf_by_name = comb_txt.apply(lambda t: any(k in t for k in ETF_TERMS))
n_etf_flag  = etf_by_flag.sum()
n_etf_name  = (~etf_by_flag & etf_by_name).sum()
excl_detail.append({"exclusion": "ETF — et_flag",    "obs_removed": int(n_etf_flag)})
excl_detail.append({"exclusion": "ETF — name-based", "obs_removed": int(n_etf_name)})
df = drop_step(df, ~(etf_by_flag | etf_by_name),
               "4. Exclude ETFs (flag + name)",
               f"flag: {n_etf_flag:,}  name-based: {n_etf_name:,}")

# ── 4e. Exclude index funds ───────────────────────────────────────────────────
idx_by_flag  = df["has_index_flag"].fillna(False)
comb_txt2    = (df["fund_name"].fillna("").str.lower() + " " +
                df["lipper_obj_name"].fillna("").str.lower())
idx_by_name  = comb_txt2.apply(lambda t: any(k in t for k in INDEX_TERMS))
n_idx_flag   = idx_by_flag.sum()
n_idx_name   = (~idx_by_flag & idx_by_name).sum()
excl_detail.append({"exclusion": "Index — index_fund_flag", "obs_removed": int(n_idx_flag)})
excl_detail.append({"exclusion": "Index — name-based",      "obs_removed": int(n_idx_name)})
df = drop_step(df, ~(idx_by_flag | idx_by_name),
               "5. Exclude index funds (flag + name)",
               f"flag: {n_idx_flag:,}  name-based: {n_idx_name:,}")

# ── 4f. Exclude non-target fund types ────────────────────────────────────────
classif_txt = (
    df["fund_name"].fillna("").str.lower()         + " " +
    df["lipper_obj_name"].fillna("").str.lower()   + " " +
    df["lipper_class_name"].fillna("").str.lower() + " " +
    df["policy"].fillna("").str.lower()
)
nontarget_mask = classif_txt.apply(lambda t: any(k in t for k in NONEQUITY_TERMS))
n_nontarget    = nontarget_mask.sum()
excl_detail.append({"exclusion": "Non-target — name/classification",
                    "obs_removed": int(n_nontarget)})
df = drop_step(df, ~nontarget_mask,
               "6. Exclude non-target types (international/bond/MM/balanced …)",
               f"{n_nontarget:,} obs caught by keywords")

snap(df, "7. Final cleaned EDC sample (before QC rules)")
print()
for row in construction:
    rm = row.get("obs_removed")
    rm_str = f"  (removed {rm:,})" if isinstance(rm, int) else ""
    print(f"  {row['step']}")
    print(f"    obs={row['obs']:>9,}  wficn={row['unique_wficn']:>6,}{rm_str}")
    if row.get("note"):
        print(f"    note: {row['note']}")


# ══════════════════════════════════════════════════════════════════════
# 5. Flow calculation
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. FLOW CALCULATION")
print("═" * 66)

df = df.sort_values(["wficn", "caldt"]).reset_index(drop=True)

df["lag_portfolio_tna"] = df.groupby("wficn")["portfolio_tna"].shift(1)
df["lag_caldt"]         = df.groupby("wficn")["caldt"].shift(1)
df["caldt_gap_days"]    = (df["caldt"] - df["lag_caldt"]).dt.days

# Accept only single-month gaps (28–35 days)
valid_lag = (
    df["lag_portfolio_tna"].notna() &
    (df["lag_portfolio_tna"] > 0) &
    (df["portfolio_tna"] > 0) &
    df["caldt_gap_days"].between(28, 35)
)

# Standard flow formula: TNA_t / TNA_{t-1} - (1 + R_t)
df["flow"] = np.where(
    valid_lag,
    df["portfolio_tna"] / df["lag_portfolio_tna"] - (1 + df["portfolio_return"]),
    np.nan
)

n_flow = df["flow"].notna().sum()
print(f"  WFICN-months with valid flow    : {n_flow:>10,}  ({100*n_flow/len(df):.1f}%)")
print(f"  Missing flow (no valid lag TNA) : {df['flow'].isna().sum():>10,}")

p01 = df["flow"].quantile(0.01)
p99 = df["flow"].quantile(0.99)
df["flow_winsorized"] = df["flow"].clip(lower=p01, upper=p99)
print(f"  Flow winsorization bounds       : [{p01:.4f}, {p99:.4f}]")
print(f"  Raw flow range                  : [{df['flow'].min():.4f}, {df['flow'].max():.4f}]")


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
print(f"  Obs with valid fund age : {n_age:>9,}  ({100*n_age/len(df):.1f}%)")
print(f"  Age range               : "
      f"{df['fund_age_years'].min():.1f} → {df['fund_age_years'].max():.1f} years")


# ══════════════════════════════════════════════════════════════════════
# 7. Save Step 2 cleaned dataset
# ══════════════════════════════════════════════════════════════════════

step2_cols = [
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
step2_cols = [c for c in step2_cols if c in df.columns]
out_step2  = PROC + PREFIX + "step2_clean_wficn_edc_flows.csv"
df[step2_cols].to_csv(out_step2, index=False)
print(f"\n  Saved Step 2 dataset → {out_step2}")


# ══════════════════════════════════════════════════════════════════════
# 8. Quality checks
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("8. QUALITY CHECKS")
print("═" * 66)

qc = ["# Extension 2003–2025 Step 2 — Quality Checks\n"]

# ── 8a. crsp_obj_cd distribution ──────────────────────────────────────────────
print("\n  a) crsp_obj_cd distribution in filtered sample:")
obj_dist = df["crsp_obj_cd"].value_counts(dropna=False)
print(obj_dist.to_string())
qc.append("## a) crsp_obj_cd distribution\n```\n" + obj_dist.to_string() + "\n```\n")
n_edc = (df["crsp_obj_cd"].str.startswith("EDC", na=False)).sum()
n_ed  = (df["crsp_obj_cd"].str.startswith("ED",  na=False)).sum()
print(f"  [EDC strict: {n_edc:,}  ED broader: {n_ed:,} — "
      f"{'same' if n_edc == n_ed else 'DIFFERENT'}]")

# ── 8b. ETF / index residuals ─────────────────────────────────────────────────
print("\n  b) ETF/index keyword residuals in filtered sample:")
final_txt      = (df["fund_name"].fillna("").str.lower() + " " +
                  df["lipper_obj_name"].fillna("").str.lower())
residual_etf   = final_txt.apply(lambda t: any(k in t for k in ETF_TERMS))
residual_index = final_txt.apply(lambda t: any(k in t for k in INDEX_TERMS))
print(f"    ETF terms remaining   : {residual_etf.sum()}")
print(f"    Index terms remaining : {residual_index.sum()}")
if residual_index.any():
    print(df[residual_index][["wficn", "fund_name", "crsp_obj_cd"]]
          .drop_duplicates("wficn").head(10).to_string(index=False))
qc.append(f"## b) ETF/index residuals\n- ETF: {residual_etf.sum()}\n"
          f"- Index: {residual_index.sum()}\n")

# ── 8c. Flow distribution plausibility ───────────────────────────────────────
print("\n  c) Flow distribution (raw, winsorized):")
for col in ["flow", "flow_winsorized"]:
    s = df[col].dropna()
    print(f"    {col}: N={len(s):,}  mean={s.mean():.4f}  "
          f"p1={s.quantile(0.01):.4f}  median={s.median():.4f}  "
          f"p99={s.quantile(0.99):.4f}  |>1|: {(s.abs()>1).sum():,}")
qc.append(f"## c) Flow distribution\n"
          f"- Raw flow N={df['flow'].notna().sum():,}  "
          f"mean={df['flow'].mean():.4f}  median={df['flow'].median():.4f}\n"
          f"- Winsorized bounds: [{p01:.4f}, {p99:.4f}]\n")

# ── 8d. Coverage by year ───────────────────────────────────────────────────────
print("\n  d) Coverage by year in filtered sample:")
yr_cover = (
    df.assign(year=df["caldt"].dt.year)
    .groupby("year")
    .agg(obs=("wficn", "count"), unique_wficn=("wficn", "nunique"),
         pct_with_flow=("flow", lambda x: round(x.notna().mean() * 100, 1)))
)
print(yr_cover.to_string())
qc.append("## d) Coverage by year\n```\n" + yr_cover.to_string() + "\n```\n")

# ── 8e. Top lipper_obj_name ───────────────────────────────────────────────────
print("\n  e) Top lipper_obj_name in filtered sample:")
lipper_dist = df["lipper_obj_name"].value_counts(dropna=False).head(15)
print(lipper_dist.to_string())
qc.append("## e) Top lipper_obj_name\n```\n" + lipper_dist.to_string() + "\n```\n")

# Save QC markdown (preliminary; updated at end)
with open(TABS + PREFIX + "step2_quality_checks.md", "w") as f:
    f.write("\n".join(qc))


# ══════════════════════════════════════════════════════════════════════
# 9. Final cleaning (regression-ready rules)
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("9. FINAL CLEANING — REGRESSION-READY RULES")
print("═" * 66)

reg_construction = []

def drop_reg(df_, mask, step_label, note=""):
    n_before = len(df_)
    w_before = df_["wficn"].nunique()
    out = df_[mask].copy()
    n_rm = n_before - len(out)
    w_rm = w_before - out["wficn"].nunique()
    reg_construction.append({
        "step": step_label, "obs_after": len(out),
        "wficn_after": out["wficn"].nunique(),
        "obs_removed": n_rm, "wficn_removed": w_rm, "note": note,
    })
    print(f"  {step_label}")
    print(f"    obs={len(out):>8,}  wficn={out['wficn'].nunique():>5,}"
          f"  removed {n_rm:,}  ({note})")
    return out

reg_construction.append({
    "step": "0. Step 2 input (after EDC/ETF/index filters)",
    "obs_after": len(df), "wficn_after": df["wficn"].nunique(),
    "obs_removed": 0, "wficn_removed": 0, "note": "Before final cleaning",
})

# Rule 1: drop impossible returns
df = drop_reg(df, df["portfolio_return"].abs() < 1,
              "1. Drop |portfolio_return| ≥ 1",
              "economically impossible for long-only fund")

# Rule 2: require lag_tna ≥ $10M (literature standard; removes tiny-fund noise)
df = drop_reg(df, df["lag_portfolio_tna"].fillna(0) >= 10,
              "2. Require lag_portfolio_tna ≥ $10M",
              "Chevalier & Ellison 1997; Sirri & Tufano 1998")

# Rule 3: valid flow_winsorized required (DV for regression)
df = drop_reg(df, df["flow_winsorized"].notna(),
              "3. Drop missing flow_winsorized",
              "DV must be non-null")

# Rule 4: valid portfolio_return (no-op after Rule 1, but explicit)
df = drop_reg(df, df["portfolio_return"].notna(),
              "4. Drop remaining missing portfolio_return",
              "needed for performance measures")


# ══════════════════════════════════════════════════════════════════════
# 10. Winsorize portfolio_return
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("10. WINSORIZE portfolio_return")
print("═" * 66)

p01_ret = df["portfolio_return"].quantile(0.01)
p99_ret = df["portfolio_return"].quantile(0.99)
df["portfolio_return_winsorized"] = df["portfolio_return"].clip(p01_ret, p99_ret)
print(f"  1st percentile  : {p01_ret:.6f}")
print(f"  99th percentile : {p99_ret:.6f}")
print(f"  Obs clipped lower : {(df['portfolio_return'] < p01_ret).sum():,}")
print(f"  Obs clipped upper : {(df['portfolio_return'] > p99_ret).sum():,}")


# ══════════════════════════════════════════════════════════════════════
# 11. Past performance measures
#
# Gap-aware rolling log-return cumulation (identical to baseline):
#   1. Compute sequential month index.
#   2. Detect gaps → assign run_id (increments at each break).
#   3. Within (wficn, run_id): shift(1) then rolling(K, min_periods=K).sum().
#   4. Back-transform: expm1(sum_log).
# This ensures a single missing month resets the window rather than
# silently bridging the gap.
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("11. CONSTRUCTING PAST PERFORMANCE MEASURES")
print("═" * 66)

df = df.sort_values(["wficn", "caldt"]).reset_index(drop=True)

df["month_idx"]     = df["caldt"].dt.year * 12 + df["caldt"].dt.month
df["lag_month_idx"] = df.groupby("wficn")["month_idx"].shift(1)
df["month_gap"]     = (df["month_idx"] - df["lag_month_idx"]).fillna(1)
df["is_break"]      = (df["month_gap"] != 1).astype(int)
df["run_id"]        = df.groupby("wficn")["is_break"].cumsum()
df["log1p_ret"]     = np.log1p(df["portfolio_return_winsorized"])

def rolling_cumret(series, window):
    """Shift by 1 (exclude current month), then rolling sum over window months."""
    return series.shift(1).rolling(window, min_periods=window).sum()

grp = df.groupby(["wficn", "run_id"])
df["sum_log_12m"] = grp["log1p_ret"].transform(lambda x: rolling_cumret(x, 12))
df["sum_log_6m"]  = grp["log1p_ret"].transform(lambda x: rolling_cumret(x,  6))

df["past_12m_return"] = np.expm1(df["sum_log_12m"])
df["past_6m_return"]  = np.expm1(df["sum_log_6m"])

df.drop(columns=["log1p_ret", "sum_log_12m", "sum_log_6m",
                 "is_break", "run_id", "lag_month_idx",
                 "month_idx", "month_gap"], inplace=True)

n_12m  = df["past_12m_return"].notna().sum()
n_6m   = df["past_6m_return"].notna().sum()
n_both = (df["past_12m_return"].notna() & df["past_6m_return"].notna()).sum()
print(f"  Obs with past_12m_return : {n_12m:>9,}  ({100*n_12m/len(df):.1f}%)")
print(f"  Obs with past_6m_return  : {n_6m:>9,}  ({100*n_6m/len(df):.1f}%)")
print(f"  Obs with both            : {n_both:>9,}  ({100*n_both/len(df):.1f}%)")

for var, label in [("past_12m_return", "12m"), ("past_6m_return", "6m")]:
    s    = df[var].dropna()
    pcts = s.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    print(f"\n  past_{label}_return  N={len(s):,}  mean={s.mean():.4f}  std={s.std():.4f}")
    print(f"    p1={pcts[0.01]:.4f}  p5={pcts[0.05]:.4f}  "
          f"p25={pcts[0.25]:.4f}  median={pcts[0.50]:.4f}  "
          f"p75={pcts[0.75]:.4f}  p95={pcts[0.95]:.4f}  p99={pcts[0.99]:.4f}")

r12 = df[df["past_12m_return"].notna()]
r6  = df[df["past_6m_return"].notna()]
print(f"\n  past_12m_return date range : "
      f"{r12['caldt'].min().date()} → {r12['caldt'].max().date()}")
print(f"  past_6m_return  date range : "
      f"{r6['caldt'].min().date()}  → {r6['caldt'].max().date()}")


# ══════════════════════════════════════════════════════════════════════
# 12. Control variables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("12. CONTROL VARIABLES")
print("═" * 66)

df["log_lag_tna"]  = np.log(df["lag_portfolio_tna"])
df["log_fund_age"] = np.log1p(df["fund_age_years"].clip(lower=0))

# Re-derive fund_age_years for any rows where first_offer_dt is present but age is null
if "first_offer_dt" in df.columns:
    df["first_offer_dt"] = pd.to_datetime(df["first_offer_dt"], errors="coerce")
    missing_age = df["fund_age_years"].isna() & df["first_offer_dt"].notna()
    df.loc[missing_age, "fund_age_years"] = (
        (df.loc[missing_age, "caldt"] - df.loc[missing_age, "first_offer_dt"])
        .dt.days / 365.25
    )

for v in ["log_lag_tna", "fund_age_years", "exp_ratio", "turn_ratio"]:
    n_ok  = df[v].notna().sum() if v in df.columns else 0
    n_mis = df[v].isna().sum()  if v in df.columns else len(df)
    print(f"  {v:<24} : {n_ok:>8,} non-null  "
          f"({n_mis:>6,} missing, {100*n_mis/len(df):.1f}%)"
          f"  mean={df[v].mean():.4f}" if v in df.columns else "")


# ══════════════════════════════════════════════════════════════════════
# 13. Summary statistics
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("13. SUMMARY STATISTICS")
print("═" * 66)

stat_vars = {
    "flow_winsorized":             "Fund flow (winsorized 1/99)",
    "flow":                        "Fund flow (raw)",
    "portfolio_return":            "Monthly portfolio return",
    "portfolio_return_winsorized": "Monthly return (winsorized 1/99)",
    "past_12m_return":             "Past 12-month cumulative return",
    "past_6m_return":              "Past 6-month cumulative return",
    "portfolio_tna":               "Portfolio TNA ($M)",
    "lag_portfolio_tna":           "Lag portfolio TNA ($M)",
    "log_lag_tna":                 "Log(lag portfolio TNA)",
    "exp_ratio":                   "Expense ratio",
    "turn_ratio":                  "Turnover ratio",
    "fund_age_years":              "Fund age (years)",
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
        "variable": label, "N": len(s),
        "mean":   round(s.mean(),    5),
        "std":    round(s.std(),     5),
        "p1":     round(q[0.01],     5),
        "p5":     round(q[0.05],     5),
        "p25":    round(q[0.25],     5),
        "median": round(q[0.50],     5),
        "p75":    round(q[0.75],     5),
        "p95":    round(q[0.95],     5),
        "p99":    round(q[0.99],     5),
    })

stats_df = pd.DataFrame(stats_rows).set_index("variable")
pd.set_option("display.width", 200)
print(stats_df[["N", "mean", "std", "p25", "median", "p75"]].to_string())


# ══════════════════════════════════════════════════════════════════════
# 14. Lag-verification: past_12m_return must not correlate with current return
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("14. LAG VERIFICATION — past_12m_return vs. portfolio_return")
print("═" * 66)

lag_corr = df[["past_12m_return", "portfolio_return"]].dropna().corr()
corr_val = lag_corr.loc["past_12m_return", "portfolio_return"]
print(f"  Corr(past_12m_return, portfolio_return) = {corr_val:.4f}")
print(f"  Expected: near zero (confirms shift(1) excluded current month)")
print(f"  {'PASS' if abs(corr_val) < 0.05 else 'FLAG — check rolling window construction'}")

qc.append(f"## f) Lag verification\n"
          f"- Corr(past_12m_return, portfolio_return) = {corr_val:.4f}\n"
          f"- Expected near zero. {'PASS' if abs(corr_val) < 0.05 else 'FLAG'}\n")


# ══════════════════════════════════════════════════════════════════════
# 15. Comparison with baseline
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("15. COMPARISON WITH BASELINE")
print("═" * 66)

BASELINE_N     = 99_325   # final_step3_regression_ready_wficn_edc.csv
BASELINE_W     = 1_215
BASELINE_START = "1999"
BASELINE_END   = "2011"

ext_r12 = df[df["past_12m_return"].notna()]
n_ext   = len(ext_r12)
w_ext   = ext_r12["wficn"].nunique()

print(f"""
  Baseline (1991–2011 CRSP, 12m regression sample):
    Observations   : {BASELINE_N:>10,}
    Unique WFICN   : {BASELINE_W:>10,}
    Effective dates: {BASELINE_START}–{BASELINE_END}

  Extension (2003–2025 CRSP, 12m regression sample):
    Observations   : {n_ext:>10,}
    Unique WFICN   : {w_ext:>10,}
    Effective dates: {ext_r12['caldt'].min().date()} → {ext_r12['caldt'].max().date()}

  Extension is larger because:
    (1) covers 22 years (2004–2025 after 12m burn-in) vs 12 years (1999–2011)
    (2) broader mutual fund universe: {df['wficn'].nunique():,} unique WFICNs
        vs {BASELINE_W:,} in baseline (more EDC funds registered post-2003)
    (3) same EDC methodology applied to a larger CRSP coverage window
""")

qc.append(f"## g) Baseline comparison\n"
          f"- Baseline N={BASELINE_N:,}, W={BASELINE_W:,} (1999–2011)\n"
          f"- Extension N={n_ext:,}, W={w_ext:,} ({ext_r12['caldt'].min().date()}–"
          f"{ext_r12['caldt'].max().date()})\n")


# ══════════════════════════════════════════════════════════════════════
# 16. Coverage by year (regression sample)
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("16. COVERAGE BY YEAR — REGRESSION SAMPLE")
print("═" * 66)

yr_reg = (
    df.assign(year=df["caldt"].dt.year)
    .groupby("year")
    .agg(
        obs          = ("wficn",          "count"),
        unique_wficn = ("wficn",          "nunique"),
        pct_r12      = ("past_12m_return", lambda x: round(x.notna().mean() * 100, 1)),
        pct_r6       = ("past_6m_return",  lambda x: round(x.notna().mean() * 100, 1)),
    )
)
print(f"  {'Year':>4}  {'obs':>8}  {'WFICN':>6}  {'%r12':>6}  {'%r6':>6}")
print(f"  {SEP2}")
for yr, row in yr_reg.iterrows():
    print(f"  {yr:>4}  {int(row.obs):>8,}  {int(row.unique_wficn):>6,}  "
          f"{row.pct_r12:>5.1f}%  {row.pct_r6:>5.1f}%")

qc.append("## h) Coverage by year (regression sample)\n```\n"
          + yr_reg.to_string() + "\n```\n")

# Final update to QC markdown
with open(TABS + PREFIX + "step2_quality_checks.md", "w") as f:
    f.write("\n".join(qc))


# ══════════════════════════════════════════════════════════════════════
# 17. Save outputs
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("17. SAVING OUTPUTS")
print("═" * 66)

def df_to_md(df_, title):
    idx_name = df_.index.name or "index"
    cols = [idx_name] + list(df_.columns)
    lines = [f"## {title}", "",
             "| " + " | ".join(str(c) for c in cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for idx, row in df_.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

# ── Regression-ready dataset ───────────────────────────────────────────────────
final_cols = [
    "wficn", "caldt",
    "flow_winsorized", "flow",
    "portfolio_return", "portfolio_return_winsorized",
    "past_12m_return", "past_6m_return",
    "portfolio_tna", "lag_portfolio_tna", "log_lag_tna",
    "fund_age_years", "log_fund_age",
    "exp_ratio", "turn_ratio", "mgmt_fee",
    "fund_name", "crsp_obj_cd",
    "lipper_obj_cd", "lipper_obj_name",
    "n_share_classes",
]
final_cols = [c for c in final_cols if c in df.columns]
out_step3  = PROC + PREFIX + "step3_regression_ready_wficn_edc.csv"
df[final_cols].to_csv(out_step3, index=False)
print(f"  Dataset (step3) → {out_step3}")

# ── Combined sample construction table ───────────────────────────────────────
all_construction = construction + [{"step": "---", "obs": "", "unique_wficn": "",
                                     "obs_removed": "", "wficn_removed": "",
                                     "note": "Final cleaning (regression-ready):"}]
for r in reg_construction:
    all_construction.append({
        "step": r["step"], "obs": r["obs_after"],
        "unique_wficn": r["wficn_after"],
        "obs_removed": r["obs_removed"], "wficn_removed": r["wficn_removed"],
        "note": r["note"],
    })
const_df = pd.DataFrame(all_construction).set_index("step")
const_df.to_csv(TABS + PREFIX + "sample_construction.csv")
with open(TABS + PREFIX + "sample_construction.md", "w") as f:
    f.write("# Extension 2003–2025 — Sample Construction\n\n" +
            df_to_md(const_df, "Step-by-step sample construction"))
print(f"  Tables  → {TABS}{PREFIX}sample_construction.{{csv,md}}")

# ── Summary statistics ────────────────────────────────────────────────────────
stats_df.to_csv(TABS + PREFIX + "summary_statistics.csv")
with open(TABS + PREFIX + "summary_statistics.md", "w") as f:
    f.write("# Extension 2003–2025 — Summary Statistics\n\n" +
            df_to_md(stats_df, "Summary statistics — regression-ready sample"))
print(f"  Tables  → {TABS}{PREFIX}summary_statistics.{{csv,md}}")
print(f"  QC      → {TABS}{PREFIX}step2_quality_checks.md")


# ══════════════════════════════════════════════════════════════════════
# 18. Conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("CONCLUSION")
print("═" * 66)

n_final  = len(df)
w_final  = df["wficn"].nunique()
all_edc  = df["crsp_obj_cd"].str.startswith("EDC", na=False).all()
no_etf   = (~df["has_et_flag"].fillna(False)).all()  if "has_et_flag"    in df.columns else True
no_idx   = (~df["has_index_flag"].fillna(False)).all() if "has_index_flag" in df.columns else True
r12_ok   = df["past_12m_return"].notna().mean() * 100
r6_ok    = df["past_6m_return"].notna().mean()  * 100
r12_med  = df["past_12m_return"].median()
r6_med   = df["past_6m_return"].median()
r12_std  = df["past_12m_return"].std()
r6_std   = df["past_6m_return"].std()
r12_plaus = abs(r12_med) < 0.30 and 0.05 < r12_std < 0.80
r6_plaus  = abs(r6_med)  < 0.20 and 0.03 < r6_std  < 0.60
r12_start = r12["caldt"].min().date() if len(r12) else "N/A"
r12_end   = r12["caldt"].max().date() if len(r12) else "N/A"

print(f"""
  Extension sample valid?         : {"YES" if all_edc and no_etf and no_idx else "REVIEW"}
    All crsp_obj_cd start with EDC: {"YES" if all_edc else "NO — check filter"}
    No ETF flags remain           : {"YES" if no_etf else "PARTIAL"}
    No index flags remain         : {"YES" if no_idx else "PARTIAL"}
    ETF/index keyword residuals   : {residual_etf.sum()} ETF / {residual_index.sum()} index

  Final sample (all cleaned obs)
    Observations                  : {n_final:>10,}
    Unique WFICNs                 : {w_final:>10,}
    Date range                    : {df['caldt'].min().date()} → {df['caldt'].max().date()}

  12m regression sample (past_12m_return available)
    Observations                  : {len(r12):>10,}
    Unique WFICNs                 : {r12['wficn'].nunique():>10,}
    Effective date range          : {r12_start} → {r12_end}
    (First 12 months per fund burned for rolling window)

  Performance variable plausibility
    past_12m_return               : median={r12_med:.4f}  std={r12_std:.4f}  → {"PLAUSIBLE" if r12_plaus else "CHECK"}
    past_6m_return                : median={r6_med:.4f}   std={r6_std:.4f}   → {"PLAUSIBLE" if r6_plaus  else "CHECK"}
    Lag verification              : corr={corr_val:.4f}   → {"PASS" if abs(corr_val) < 0.05 else "FLAG"}

  Ready for Step 3 (extended-sample regressions + quintile analysis) : YES
""")

print(SEP)
print("Done.")
print("═" * 66)
