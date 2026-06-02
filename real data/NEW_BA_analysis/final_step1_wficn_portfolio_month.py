"""
Final Step 1 — WFICN-based portfolio-month dataset (1991-2011)
Observation level: wficn × caldt

Uses MFLinks WFICN as the portfolio identifier instead of crsp_portno,
because crsp_portno coverage is sparse before 2003 while WFICN covers
active EDC funds at ~93-99% across the full 1991-2011 window.

No fund-type filters, no flow calculation, no regressions.
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

SEP  = "\n" + "═" * 64
SEP2 = "─" * 64


# ══════════════════════════════════════════════════════════════════════
# 1. Load files
# ══════════════════════════════════════════════════════════════════════

print("Loading raw files …")

ret = pd.read_csv(RAW + "monthly_returns_1991_2011.csv",        low_memory=False)
fsq = pd.read_csv(RAW + "fund_summary_quarterly_1991_2011.csv", low_memory=False)
mfl = pd.read_csv(RAW + "mflinks_crsp_fundno_wficn.csv",       low_memory=False)

# Normalise column names
for df in (ret, fsq, mfl):
    df.columns = df.columns.str.lower().str.strip()

ret["caldt"] = pd.to_datetime(ret["caldt"])
fsq["caldt"] = pd.to_datetime(fsq["caldt"])

# Force numeric; mret can contain codes like 'R' (reinvestment-only months)
ret["mret"] = pd.to_numeric(ret["mret"], errors="coerce")
ret["mtna"] = pd.to_numeric(ret["mtna"], errors="coerce")
ret["year"] = ret["caldt"].dt.year

n_raw = len(ret)

print(SEP)
print("1. BASIC DIAGNOSTICS")
print("═" * 64)

print(f"\n  monthly_returns_1991_2011")
print(f"    rows          : {n_raw:>10,}")
print(f"    columns       : {ret.columns.tolist()}")
print(f"    date range    : {ret['caldt'].min().date()} → {ret['caldt'].max().date()}")
print(f"    unique fundno : {ret['crsp_fundno'].nunique():>9,}")

print(f"\n  fund_summary_quarterly_1991_2011")
print(f"    rows          : {len(fsq):>10,}")
print(f"    columns       : {fsq.columns.tolist()}")
print(f"    date range    : {fsq['caldt'].min().date()} → {fsq['caldt'].max().date()}")
print(f"    unique fundno : {fsq['crsp_fundno'].nunique():>9,}")

print(f"\n  mflinks_crsp_fundno_wficn")
print(f"    rows          : {len(mfl):>10,}")
print(f"    columns       : {mfl.columns.tolist()}")
print(f"    unique fundno : {mfl['crsp_fundno'].nunique():>9,}")
print(f"    unique wficn  : {mfl['wficn'].nunique():>9,}")


# ══════════════════════════════════════════════════════════════════════
# 2. Map crsp_fundno → WFICN
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. MAPPING crsp_fundno → WFICN")
print("═" * 64)

# MFLinks is static (no date range), so the merge is unconditional.
# ~341 fundnos have multiple WFICN entries (fund was reassigned across
# time). Use the modal WFICN — the one that appears most often for that
# fundno, which is typically the surviving/primary portfolio.
wficn_canonical = (
    mfl.groupby("crsp_fundno")["wficn"]
    .agg(lambda x: x.mode().iloc[0])
    .reset_index()
)

mapped   = ret.merge(wficn_canonical, on="crsp_fundno", how="inner")
unmapped = ret[~ret["crsp_fundno"].isin(wficn_canonical["crsp_fundno"])].copy()

n_mapped   = len(mapped)
n_unmapped = len(unmapped)

print(f"\n  Raw observations         : {n_raw:>10,}")
print(f"  Mapped (have WFICN)      : {n_mapped:>10,}  ({100*n_mapped/n_raw:.1f}%)")
print(f"  Unmapped (no WFICN)      : {n_unmapped:>10,}  ({100*n_unmapped/n_raw:.1f}%)")
print(f"\n  Unique crsp_fundno mapped : {mapped['crsp_fundno'].nunique():>9,}")
print(f"  Unique WFICN after merge  : {mapped['wficn'].nunique():>9,}")

# Coverage by year
by_year_map = (
    ret.assign(has_wficn=ret["crsp_fundno"].isin(wficn_canonical["crsp_fundno"]))
    .groupby("year")
    .agg(
        total_obs    = ("crsp_fundno", "count"),
        mapped_obs   = ("has_wficn",   "sum"),
        unmapped_obs = ("has_wficn",   lambda x: (~x).sum()),
    )
    .assign(pct_mapped=lambda d: (d["mapped_obs"] / d["total_obs"] * 100).round(1))
)

print(f"\n  {'Year':>4}  {'Total':>9}  {'Mapped':>9}  {'Unmapped':>9}  {'%Mapped':>8}")
print(f"  {SEP2}")
for yr, row in by_year_map.iterrows():
    print(f"  {yr:>4}  {int(row.total_obs):>9,}  "
          f"{int(row.mapped_obs):>9,}  {int(row.unmapped_obs):>9,}  "
          f"{row.pct_mapped:>7.1f}%")

# Sub-period summary
print(f"\n  {'Period':<16}  {'Obs':>9}  {'%Mapped':>8}")
print(f"  {SEP2}")
for label, mask in [
    ("1991–2011", ret["year"].between(1991,2011)),
    ("1997–2011", ret["year"].between(1997,2011)),
    ("2003–2011", ret["year"].between(2003,2011)),
]:
    sub = ret[mask]
    pct = sub["crsp_fundno"].isin(wficn_canonical["crsp_fundno"]).mean() * 100
    print(f"  {label:<16}  {len(sub):>9,}  {pct:>7.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 3. Aggregate share classes → WFICN-month
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. AGGREGATING TO WFICN-MONTH LEVEL")
print("═" * 64)

# Drop rows with missing TNA — weight is undefined, cannot include in average
mapped_clean = mapped.dropna(subset=["mtna"]).copy()
n_dropped_tna = n_mapped - len(mapped_clean)
print(f"\n  Rows dropped (mtna NaN)   : {n_dropped_tna:>10,}")
print(f"  Rows used for aggregation : {len(mapped_clean):>10,}")

# Vectorised TNA-weighted return
#   numerator   = sum(mret_i × mtna_i)  over valid (mret notna, mtna > 0) rows
#   denominator = sum(mtna_i)            over the same valid rows
# Rows where mret is NaN contribute to portfolio_tna but not portfolio_return.
# min_count=1 ensures the result is NaN (not 0) if all values are NaN.

valid_for_return = mapped_clean["mret"].notna() & (mapped_clean["mtna"] > 0)

mapped_clean["ret_x_tna"]   = np.where(valid_for_return,
                                        mapped_clean["mret"] * mapped_clean["mtna"],
                                        np.nan)
mapped_clean["tna_for_ret"] = np.where(valid_for_return,
                                        mapped_clean["mtna"],
                                        np.nan)
mapped_clean["valid_sc"]    = valid_for_return.astype(int)

grp = mapped_clean.groupby(["wficn", "caldt"])

agg = pd.DataFrame({
    "portfolio_tna"                     : grp["mtna"].sum(),
    "ret_num"                           : grp["ret_x_tna"].sum(min_count=1),
    "ret_den"                           : grp["tna_for_ret"].sum(min_count=1),
    "n_share_classes"                   : grp["crsp_fundno"].count(),
    "n_valid_share_classes_for_return"  : grp["valid_sc"].sum(),
}).reset_index()

agg["portfolio_return"] = agg["ret_num"] / agg["ret_den"]
agg = agg.drop(columns=["ret_num", "ret_den"])

n_final = len(agg)
print(f"\n  WFICN-month observations  : {n_final:>10,}")
print(f"  Unique WFICN              : {agg['wficn'].nunique():>9,}")
print(f"  Date range                : "
      f"{agg['caldt'].min().date()} → {agg['caldt'].max().date()}")
print(f"  Avg share classes / WFICN-month : {agg['n_share_classes'].mean():.2f}")
print(f"  Max share classes / WFICN-month : {int(agg['n_share_classes'].max()):,}")
print(f"  WFICN-months with missing return: "
      f"{agg['portfolio_return'].isna().sum():,}")


# ══════════════════════════════════════════════════════════════════════
# 4. Save output
# ══════════════════════════════════════════════════════════════════════

out_path = PROC + "final_step1_wficn_portfolio_month.csv"
agg.to_csv(out_path, index=False)
print(f"\n  Saved → {out_path}")


# ══════════════════════════════════════════════════════════════════════
# 5. Diagnostic tables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. DIAGNOSTIC SUMMARY")
print("═" * 64)

# ── 5a. Overall summary ────────────────────────────────────────────────────────
summary_rows = [
    ("Raw monthly return observations",           n_raw),
    ("Mapped observations (have WFICN)",           n_mapped),
    ("Unmapped observations (no WFICN)",           n_unmapped),
    ("Unique crsp_fundno before aggregation",      mapped["crsp_fundno"].nunique()),
    ("Unique WFICN after mapping",                 mapped["wficn"].nunique()),
    ("Rows dropped (mtna NaN)",                    n_dropped_tna),
    ("Final WFICN-month observations",             n_final),
    ("Average share classes per WFICN-month",      round(agg["n_share_classes"].mean(), 2)),
    ("Maximum share classes per WFICN-month",      int(agg["n_share_classes"].max())),
    ("WFICN-months with missing portfolio_return", agg["portfolio_return"].isna().sum()),
]

print()
for label, val in summary_rows:
    print(f"  {label:<48} : {val:>10}")

# ── 5b. Mapping coverage by year (for the diagnostic CSV) ─────────────────────
diag_yr = by_year_map.copy()
diag_yr.index.name = "year"

# Also compute final WFICN-month counts by year
wficn_yr = (
    agg.assign(year=pd.to_datetime(agg["caldt"]).dt.year)
    .groupby("year")
    .agg(wficn_month_obs=("wficn","count"),
         unique_wficn=("wficn","nunique"))
)
diag_yr = diag_yr.join(wficn_yr, how="left")

print(f"\n  {'Year':>4}  {'Total':>9}  {'Mapped':>9}  {'%Mapped':>8}  "
      f"{'WFICN-mo':>9}  {'Uniq WFICN':>11}")
print(f"  {SEP2}")
for yr, row in diag_yr.iterrows():
    wm  = int(row.get("wficn_month_obs", 0) or 0)
    uwf = int(row.get("unique_wficn",    0) or 0)
    print(f"  {yr:>4}  {int(row.total_obs):>9,}  "
          f"{int(row.mapped_obs):>9,}  {row.pct_mapped:>7.1f}%  "
          f"{wm:>9,}  {uwf:>11,}")

# ── 5c. Save diagnostic CSV ────────────────────────────────────────────────────
diag_yr.to_csv(TABS + "final_step1_wficn_mapping_diagnostics.csv")
print(f"\n  Saved CSV → {TABS}final_step1_wficn_mapping_diagnostics.csv")

# ── 5d. Save diagnostic markdown ──────────────────────────────────────────────
def df_to_md(df, title):
    idx_name = df.index.name or "index"
    cols     = [idx_name] + df.columns.tolist()
    sep_row  = "| " + " | ".join(["---"] * len(cols)) + " |"
    lines    = [f"## {title}", "",
                "| " + " | ".join(str(c) for c in cols) + " |",
                sep_row]
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

summary_df = pd.DataFrame(summary_rows, columns=["metric","value"]).set_index("metric")

md_content = (
    "# Final Step 1 — WFICN Portfolio-Month Dataset: Mapping Diagnostics\n\n"
    + df_to_md(summary_df,
               "Table A — Overall summary") + "\n\n"
    + df_to_md(diag_yr[["total_obs","mapped_obs","unmapped_obs","pct_mapped",
                         "wficn_month_obs","unique_wficn"]],
               "Table B — Mapping coverage and WFICN-month counts by year")
    + "\n"
)

md_path = TABS + "final_step1_wficn_mapping_diagnostics.md"
with open(md_path, "w") as f:
    f.write(md_content)
print(f"  Saved  MD → {md_path}")

print(SEP)
print("Done.")
print("═" * 64)
