"""
Step 1 — Unmapped observations diagnostic
Reproduces the same mapping logic as guide_step1_portfolio_month.py and then
analyses only the observations that could not be assigned a crsp_portno.
Does NOT modify the Step 1 output file.
"""

import pandas as pd
import numpy as np

RAW = (
    "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit"
    "/real data/real, clear data/raw/new data/"
)

# ── Load raw files ─────────────────────────────────────────────────────────────

print("Loading raw files …")
ret  = pd.read_csv(RAW + "monthly_returns_1991_2011.csv",          low_memory=False)
pmap = pd.read_csv(RAW + "fund_portfolio_map_1991_2011.csv",       low_memory=False)
fsq  = pd.read_csv(RAW + "fund_summary_quarterly_1991_2011.csv",   low_memory=False)

ret["caldt"]   = pd.to_datetime(ret["caldt"])
pmap["begdt"]  = pd.to_datetime(pmap["begdt"])
pmap["enddt"]  = pd.to_datetime(pmap["enddt"])
ret["year"]    = ret["caldt"].dt.year
ret["mtna"]    = pd.to_numeric(ret["mtna"], errors="coerce")

# ── Replicate Step 1 mapping to get mapped / unmapped labels ──────────────────

print("Reproducing tiered mapping …")

portno_counts        = pmap.groupby("crsp_fundno")["crsp_portno"].nunique()
single_portno_fundno = set(portno_counts[portno_counts == 1].index)
multi_portno_fundno  = set(portno_counts[portno_counts > 1].index)
all_map_fundno       = set(pmap["crsp_fundno"])

# Single-portno: always mappable
ret_single = ret[ret["crsp_fundno"].isin(single_portno_fundno)].copy()
ret_single["mapped"] = True

# Multi-portno: mapped only if caldt falls within a recorded [begdt, enddt]
multi_map = pmap[pmap["crsp_fundno"].isin(multi_portno_fundno)][
    ["crsp_fundno", "crsp_portno", "begdt", "enddt"]
]
ret_multi_all = ret[ret["crsp_fundno"].isin(multi_portno_fundno)].copy()
merged_multi  = ret_multi_all.merge(multi_map, on="crsp_fundno", how="left")
valid_date    = (merged_multi["caldt"] >= merged_multi["begdt"]) & (
    merged_multi["caldt"].le(merged_multi["enddt"]) | merged_multi["enddt"].isna()
)
# Observations that matched at least one valid date window
mapped_multi_idx = set(
    merged_multi.loc[valid_date, ["crsp_fundno", "caldt"]]
    .apply(tuple, axis=1)
)
ret_multi_all["mapped"] = ret_multi_all.apply(
    lambda r: (r["crsp_fundno"], r["caldt"]) in mapped_multi_idx, axis=1
)

# Not-in-map: never mappable
ret_nomap = ret[~ret["crsp_fundno"].isin(all_map_fundno)].copy()
ret_nomap["mapped"] = False

# Full labelled dataset
full = pd.concat([ret_single, ret_multi_all, ret_nomap], ignore_index=True)

n_total   = len(full)
n_mapped  = full["mapped"].sum()
n_unmapped = (~full["mapped"]).sum()
print(f"  Total: {n_total:,}  |  Mapped: {n_mapped:,}  |  Unmapped: {n_unmapped:,}")

unmapped = full[~full["mapped"]].copy()
mapped_df = full[full["mapped"]].copy()

# ── Bucket the unmapped by root cause ─────────────────────────────────────────
not_in_map     = unmapped[~unmapped["crsp_fundno"].isin(all_map_fundno)]
in_map_outside = unmapped[ unmapped["crsp_fundno"].isin(all_map_fundno)]

SEP = "\n" + "─" * 62

# ══════════════════════════════════════════════════════════════════
# 1. Unmapped observations by year
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("1. UNMAPPED OBSERVATIONS BY YEAR")
print("─" * 62)

by_year = (
    full.groupby("year")["mapped"]
    .agg(
        total="count",
        mapped_n="sum",
    )
    .assign(
        unmapped_n=lambda d: d["total"] - d["mapped_n"],
        mapped_pct=lambda d: (d["mapped_n"] / d["total"] * 100).round(1),
        unmapped_pct=lambda d: (d["unmapped_n"] / d["total"] * 100).round(1),
    )
)
print(by_year[["total", "mapped_n", "mapped_pct", "unmapped_n", "unmapped_pct"]].to_string())

# ══════════════════════════════════════════════════════════════════
# 2. Pre-1997 vs 1997-onward split
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("3. PRE-1997 vs 1997-ONWARD  (earliest begdt in map: 1997-03-31)")
print("─" * 62)

for label, mask in [("Pre-1997",   full["year"] < 1997),
                    ("1997–2011",  full["year"] >= 1997)]:
    sub = full[mask]
    um  = (~sub["mapped"]).sum()
    tot = len(sub)
    print(f"  {label:<12}  total={tot:>10,}  unmapped={um:>9,}  "
          f"unmapped_rate={100*um/tot:.1f}%")

# ══════════════════════════════════════════════════════════════════
# 3. TNA: mapped vs unmapped
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("4. AVERAGE AND MEDIAN MTNA: MAPPED vs UNMAPPED  ($ millions)")
print("─" * 62)

for label, df in [("Mapped",   mapped_df),
                  ("Unmapped", unmapped)]:
    tna = df["mtna"].dropna()
    print(f"  {label:<10}  N={len(tna):>9,}  mean={tna.mean():>9.2f}  "
          f"median={tna.median():>8.2f}  p75={tna.quantile(.75):>8.2f}  "
          f"p95={tna.quantile(.95):>8.2f}")

# ══════════════════════════════════════════════════════════════════
# 4. Top-20 unmapped crsp_fundno by total mtna
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("5. TOP 20 UNMAPPED crsp_fundno BY TOTAL MTNA")
print("─" * 62)

# Get a representative fund name from fund_summary (most recent row per fundno)
fsq_names = (
    fsq.sort_values("caldt")
    .drop_duplicates(subset="crsp_fundno", keep="last")
    [["crsp_fundno", "fund_name", "lipper_asset_cd", "lipper_obj_cd", "lipper_obj_name"]]
)

top20 = (
    unmapped.groupby("crsp_fundno")["mtna"]
    .sum()
    .sort_values(ascending=False)
    .head(20)
    .reset_index()
    .rename(columns={"mtna": "total_mtna_$M"})
    .merge(fsq_names, on="crsp_fundno", how="left")
)
print(top20.to_string(index=False))

# ══════════════════════════════════════════════════════════════════
# 5. Asset-class breakdown of unmapped observations
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("6. ASSET CLASS OF UNMAPPED FUNDS  (via fund_summary_quarterly)")
print("─" * 62)

# Build a per-fundno classification from fund_summary (mode of lipper_asset_cd)
fsq_class = (
    fsq[fsq["lipper_asset_cd"].notna()]
    .groupby("crsp_fundno")["lipper_asset_cd"]
    .agg(lambda x: x.mode().iloc[0])
    .reset_index()
    .rename(columns={"lipper_asset_cd": "asset_class"})
)
fsq_objname = (
    fsq[fsq["lipper_obj_name"].notna()]
    .groupby("crsp_fundno")["lipper_obj_name"]
    .agg(lambda x: x.mode().iloc[0])
    .reset_index()
    .rename(columns={"lipper_obj_name": "lipper_obj_name_mode"})
)

unmapped_class = (
    unmapped[["crsp_fundno"]].drop_duplicates()
    .merge(fsq_class, on="crsp_fundno", how="left")
)
print("\n  a) lipper_asset_cd distribution among unmapped FUNDS:")
asset_dist = unmapped_class["asset_class"].value_counts(dropna=False)
asset_dist_pct = (asset_dist / asset_dist.sum() * 100).round(1)
print(pd.DataFrame({"funds": asset_dist, "pct": asset_dist_pct}).to_string())

# Obs-level: attach asset_class to unmapped observations
unmapped_w_class = unmapped.merge(fsq_class, on="crsp_fundno", how="left")
print("\n  b) lipper_asset_cd distribution by OBSERVATION COUNT:")
obs_dist = unmapped_w_class["asset_class"].value_counts(dropna=False)
obs_pct  = (obs_dist / obs_dist.sum() * 100).round(1)
print(pd.DataFrame({"obs": obs_dist, "pct": obs_pct}).to_string())

print("\n  c) lipper_asset_cd distribution by TOTAL MTNA ($ millions):")
tna_by_class = (
    unmapped_w_class.groupby("asset_class", dropna=False)["mtna"]
    .sum()
    .sort_values(ascending=False)
)
tna_pct = (tna_by_class / tna_by_class.sum() * 100).round(1)
print(pd.DataFrame({"total_mtna_$M": tna_by_class.round(0), "pct": tna_pct}).to_string())

# ── Equity sub-classification for unmapped EQ funds ───────────────────────────
print("\n  d) lipper_obj_name for UNMAPPED EQUITY (EQ) observations:")
unmapped_eq = unmapped_w_class[unmapped_w_class["asset_class"] == "EQ"]
unmapped_eq_obj = unmapped_eq.merge(fsq_objname, on="crsp_fundno", how="left")
obj_dist = unmapped_eq_obj["lipper_obj_name_mode"].value_counts(dropna=False).head(20)
obj_pct  = (obj_dist / obj_dist.sum() * 100).round(1)
print(pd.DataFrame({"obs": obj_dist, "pct": obj_pct}).to_string())

# ── Root-cause summary ─────────────────────────────────────────────────────────
print(SEP)
print("ROOT-CAUSE BREAKDOWN OF UNMAPPED OBSERVATIONS")
print("─" * 62)
print(f"  Not in fund_portfolio_map at all          : "
      f"{len(not_in_map):>9,}  ({100*len(not_in_map)/n_unmapped:.1f}%)")
print(f"  In map but caldt outside begdt/enddt      : "
      f"{len(in_map_outside):>9,}  ({100*len(in_map_outside)/n_unmapped:.1f}%)")
print(f"  Total unmapped                            : "
      f"{n_unmapped:>9,}")
print("─" * 62)
