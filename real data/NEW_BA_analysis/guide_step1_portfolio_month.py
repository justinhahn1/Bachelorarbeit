"""
Step 1: Build portfolio-month base dataset (1991-2011)
Observation level: crsp_portno × caldt
No fund-type filters, no flow calculation, no regressions.

Mapping strategy for crsp_fundno → crsp_portno:
  - Single-portno share classes: assign portno regardless of date (CRSP only
    recorded begdt from 2003 onward for many older funds, but the portno itself
    is unambiguous).
  - Multi-portno share classes (fund moved between portfolios): apply the
    date filter caldt ∈ [begdt, enddt] to pick the correct portno.
"""

import pandas as pd
import numpy as np

RAW = (
    "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit"
    "/real data/real, clear data/raw/new data/"
)
OUT = (
    "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit"
    "/real data/NEW_BA_analysis/data/processed/"
)

# ── 1. Load raw files ──────────────────────────────────────────────────────────

print("Loading raw files …")

ret = pd.read_csv(RAW + "monthly_returns_1991_2011.csv", low_memory=False)
pmap = pd.read_csv(RAW + "fund_portfolio_map_1991_2011.csv", low_memory=False)
fsq = pd.read_csv(RAW + "fund_summary_quarterly_1991_2011.csv", low_memory=False)

ret["caldt"]   = pd.to_datetime(ret["caldt"])
pmap["begdt"]  = pd.to_datetime(pmap["begdt"])
pmap["enddt"]  = pd.to_datetime(pmap["enddt"])   # NaT where missing
fsq["caldt"]   = pd.to_datetime(fsq["caldt"])

print("\n=== monthly_returns_1991_2011 ===")
print("Columns    :", ret.columns.tolist())
print("Rows       :", f"{len(ret):,}")
print("Date range :", ret["caldt"].min().date(), "→", ret["caldt"].max().date())
print("Unique crsp_fundno:", f"{ret['crsp_fundno'].nunique():,}")

print("\n=== fund_portfolio_map_1991_2011 ===")
print("Columns    :", pmap.columns.tolist())
print("Rows       :", f"{len(pmap):,}")
print("begdt range:", pmap["begdt"].min().date(), "→", pmap["begdt"].max().date())
print("enddt range:", pmap["enddt"].min().date(), "→", pmap["enddt"].max().date())
print("Unique crsp_fundno:", f"{pmap['crsp_fundno'].nunique():,}")
print("Unique crsp_portno:", f"{pmap['crsp_portno'].nunique():,}")

print("\n=== fund_summary_quarterly_1991_2011 ===")
print("Columns    :", fsq.columns.tolist())
print("Rows       :", f"{len(fsq):,}")
print("Date range :", fsq["caldt"].min().date(), "→", fsq["caldt"].max().date())
print("Unique crsp_fundno:", f"{fsq['crsp_fundno'].nunique():,}")
if "crsp_portno" in fsq.columns:
    print("Unique crsp_portno:", f"{fsq['crsp_portno'].nunique():,}")

n_raw = len(ret)

# ── 2. Build a tiered crsp_fundno → crsp_portno mapping ───────────────────────

print("\n─── Building tiered portfolio mapping ───")

# Count how many distinct portnos each fundno has in the map
portno_counts = pmap.groupby("crsp_fundno")["crsp_portno"].nunique()

single_portno_fundnos = portno_counts[portno_counts == 1].index
multi_portno_fundnos  = portno_counts[portno_counts > 1].index

print(f"  Single-portno share classes : {len(single_portno_fundnos):,}")
print(f"  Multi-portno  share classes : {len(multi_portno_fundnos):,}")

# ── 2a. Single-portno: date-free lookup ───────────────────────────────────────
# These fundnos have exactly one portfolio; CRSP's begdt just reflects when
# the record was entered, not when the relationship started.
single_map = (
    pmap[pmap["crsp_fundno"].isin(single_portno_fundnos)]
    [["crsp_fundno", "crsp_portno"]]
    .drop_duplicates(subset="crsp_fundno")
)

ret_single = ret[ret["crsp_fundno"].isin(single_portno_fundnos)].merge(
    single_map, on="crsp_fundno", how="left"
)

# ── 2b. Multi-portno: strict date filter ──────────────────────────────────────
# Fund moved between portfolios; apply [begdt, enddt] to get the right portno.
multi_map = pmap[pmap["crsp_fundno"].isin(multi_portno_fundnos)][
    ["crsp_fundno", "crsp_portno", "begdt", "enddt"]
].copy()

ret_multi_raw = ret[ret["crsp_fundno"].isin(multi_portno_fundnos)]
ret_multi = ret_multi_raw.merge(multi_map, on="crsp_fundno", how="left")

valid_date = (ret_multi["caldt"] >= ret_multi["begdt"]) & (
    ret_multi["caldt"].le(ret_multi["enddt"]) | ret_multi["enddt"].isna()
)
ret_multi = ret_multi[valid_date].drop(columns=["begdt", "enddt"])

# Drop any duplicate (fundno, caldt) rows from overlapping map date ranges
dups = ret_multi.duplicated(subset=["crsp_fundno", "caldt"], keep=False)
if dups.any():
    print(f"  WARNING: {dups.sum()} duplicate (fundno, caldt) rows in multi-portno "
          "set — keeping first match.")
    ret_multi = ret_multi.drop_duplicates(subset=["crsp_fundno", "caldt"], keep="first")

# ── 2c. Unmapped: fundnos not in the map at all ───────────────────────────────
mapped_fundnos = set(pmap["crsp_fundno"])
ret_unmapped = ret[~ret["crsp_fundno"].isin(mapped_fundnos)].copy()
ret_unmapped["crsp_portno"] = np.nan

# ── 2d. Combine ───────────────────────────────────────────────────────────────
mapped = pd.concat(
    [ret_single, ret_multi],
    ignore_index=True
)

n_mapped   = len(mapped)
n_unmapped = n_raw - n_mapped

print(f"\n  Raw observations             : {n_raw:>10,}")
print(f"  Mapped (single-portno path)  : {len(ret_single):>10,}")
print(f"  Mapped (multi-portno path)   : {len(ret_multi):>10,}")
print(f"  Total mapped                 : {n_mapped:>10,}")
print(f"  Unmapped (no map entry)      : {n_unmapped:>10,}  ({100*n_unmapped/n_raw:.2f}%)")
print(f"  Date range of mapped obs     : "
      f"{mapped['caldt'].min().date()} → {mapped['caldt'].max().date()}")

# ── 3. Clean numeric columns before aggregation ───────────────────────────────

# mret may contain non-numeric codes (e.g. 'R'), force numeric
mapped["mret"] = pd.to_numeric(mapped["mret"], errors="coerce")
mapped["mtna"] = pd.to_numeric(mapped["mtna"],  errors="coerce")

# Drop rows with no TNA — cannot compute TNA-weighted return without a weight
mapped = mapped.dropna(subset=["mtna"])

# ── 4. Aggregate share classes → portfolio-month ──────────────────────────────

print("\n─── Aggregating to portfolio-month level ───")

# Vectorised TNA-weighted return:
#   numerator   = sum(mret_i * mtna_i)  — only where mret is not NaN
#   denominator = sum(mtna_i)           — only where mret is not NaN
# Using a separate "valid" mask keeps portfolio_return NaN when no share class
# has both a valid mret and a positive weight.

valid = mapped["mret"].notna() & (mapped["mtna"] > 0)
mapped["ret_x_tna"] = np.where(valid, mapped["mret"] * mapped["mtna"], np.nan)
mapped["tna_for_ret"] = np.where(valid, mapped["mtna"], np.nan)

grp = mapped.groupby(["crsp_portno", "caldt"])

agg = pd.DataFrame({
    "portfolio_tna":    grp["mtna"].sum(),
    "ret_numerator":    grp["ret_x_tna"].sum(min_count=1),   # NaN if all NaN
    "ret_denominator":  grp["tna_for_ret"].sum(min_count=1), # NaN if all NaN
    "n_share_classes":  grp["crsp_fundno"].count(),
}).reset_index()

agg["portfolio_return"] = agg["ret_numerator"] / agg["ret_denominator"]
agg = agg.drop(columns=["ret_numerator", "ret_denominator"])

print(f"  Portfolio-month observations : {len(agg):>10,}")
print(f"  Unique crsp_portno           : {agg['crsp_portno'].nunique():>10,}")
print(f"  Date range                   : "
      f"{agg['caldt'].min().date()} → {agg['caldt'].max().date()}")

# ── 5. Save output ─────────────────────────────────────────────────────────────

out_path = OUT + "guide_step1_portfolio_month_1991_2011.csv"
agg.to_csv(out_path, index=False)
print(f"\nSaved → {out_path}")

# ── 6. Diagnostic summary ──────────────────────────────────────────────────────

print("\n" + "=" * 62)
print("DIAGNOSTIC SUMMARY")
print("=" * 62)
print(f"  Raw monthly return observations    : {n_raw:>10,}")
print(f"  Mapped observations                : {n_mapped:>10,}")
print(f"  Unmapped observations              : {n_unmapped:>10,}  ({100*n_unmapped/n_raw:.1f}%)")
print(f"  Unique crsp_fundno (before agg.)   : {mapped['crsp_fundno'].nunique():>10,}")
print(f"  Unique crsp_portno (after mapping) : {mapped['crsp_portno'].nunique():>10,}")
print(f"  Final portfolio-month observations : {len(agg):>10,}")
print(f"  Avg share classes per port.-month  : {agg['n_share_classes'].mean():>10.2f}")
print(f"  Max share classes per port.-month  : {int(agg['n_share_classes'].max()):>10,}")
print(f"  Date range of final dataset        : "
      f"{agg['caldt'].min().date()} → {agg['caldt'].max().date()}")
print("=" * 62)
