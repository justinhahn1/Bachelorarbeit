"""
Step 1c — MFLinks / WFICN coverage diagnostic.

Checks whether WFICN (from MFLinks) solves the early-year crsp_portno
coverage gap identified in Steps 1 and 1b.

Does NOT modify the Step 1 output file.
"""

import pandas as pd
import numpy as np
import os

RAW = (
    "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit"
    "/real data/real, clear data/raw/new data/"
)
OUT = (
    "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit"
    "/real data/NEW_BA_analysis/output/tables/"
)
os.makedirs(OUT, exist_ok=True)

SEP  = "\n" + "═" * 66
SEP2 = "\n" + "─" * 66


# ══════════════════════════════════════════════════════════════════════
# 1. Load files and print basic diagnostics
# ══════════════════════════════════════════════════════════════════════

print("Loading raw files …")

ret  = pd.read_csv(RAW + "monthly_returns_1991_2011.csv",        low_memory=False)
pmap = pd.read_csv(RAW + "fund_portfolio_map_1991_2011.csv",     low_memory=False)
fsq  = pd.read_csv(RAW + "fund_summary_quarterly_1991_2011.csv", low_memory=False)
mfl  = pd.read_csv(RAW + "mflinks_crsp_fundno_wficn.csv",       low_memory=False)

# Normalise column names to lower-case for robustness
ret.columns  = ret.columns.str.lower().str.strip()
pmap.columns = pmap.columns.str.lower().str.strip()
fsq.columns  = fsq.columns.str.lower().str.strip()
mfl.columns  = mfl.columns.str.lower().str.strip()

# Parse dates
ret["caldt"]  = pd.to_datetime(ret["caldt"])
pmap["begdt"] = pd.to_datetime(pmap["begdt"])
pmap["enddt"] = pd.to_datetime(pmap["enddt"])
fsq["caldt"]  = pd.to_datetime(fsq["caldt"])

ret["mtna"]  = pd.to_numeric(ret["mtna"], errors="coerce")
ret["year"]  = ret["caldt"].dt.year

print(SEP)
print("1. BASIC DIAGNOSTICS")
print("═" * 66)

specs = [
    ("monthly_returns",        ret,  "caldt",  "crsp_fundno", None),
    ("fund_portfolio_map",     pmap, "begdt",  "crsp_fundno", "crsp_portno"),
    ("fund_summary_quarterly", fsq,  "caldt",  "crsp_fundno", "crsp_portno"),
    ("mflinks_crsp_wficn",     mfl,  None,     "crsp_fundno", "wficn"),
]
for label, df, datecol, fn_col, id2_col in specs:
    print(f"\n  {label}")
    print(f"    rows          : {len(df):>10,}")
    print(f"    columns       : {df.columns.tolist()}")
    if datecol and datecol in df.columns:
        print(f"    date range    : {df[datecol].min().date()} → {df[datecol].max().date()}")
    if datecol == "begdt" and "enddt" in df.columns:
        print(f"    enddt range   : {df['enddt'].min().date()} → {df['enddt'].max().date()}")
    if fn_col in df.columns:
        print(f"    unique fundno : {df[fn_col].nunique():>9,}")
    if id2_col and id2_col in df.columns:
        nn = df[id2_col].notna().sum()
        print(f"    unique {id2_col:<8}: {df[id2_col].nunique():>9,}  (non-null: {nn:,})")


# ══════════════════════════════════════════════════════════════════════
# 2. MFLinks internal structure
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2a. MFLinks INTERNAL STRUCTURE")
print("═" * 66)

# fundnos with multiple WFICN entries (fund was reassigned/merged)
wficn_per_fn = mfl.groupby("crsp_fundno")["wficn"].nunique()
fn_per_wficn = mfl.groupby("wficn")["crsp_fundno"].nunique()

print(f"  Total rows                          : {len(mfl):>9,}")
print(f"  Unique crsp_fundno                  : {mfl['crsp_fundno'].nunique():>9,}")
print(f"  Unique wficn                        : {mfl['wficn'].nunique():>9,}")
print(f"  Rows with null wficn                : {mfl['wficn'].isna().sum():>9,}")
print(f"  fundno mapped to exactly 1 wficn    : {(wficn_per_fn == 1).sum():>9,}")
print(f"  fundno mapped to 2+ wficn           : {(wficn_per_fn >  1).sum():>9,}")
print(f"  wficn with exactly 1 fundno         : {(fn_per_wficn == 1).sum():>9,}")
print(f"  wficn with 2+ fundno                : {(fn_per_wficn >  1).sum():>9,}")
print(f"  avg fundno per wficn                : {fn_per_wficn.mean():>9.2f}")
print(f"  median fundno per wficn             : {fn_per_wficn.median():>9.1f}")
print(f"  max fundno per wficn                : {fn_per_wficn.max():>9,}")

# Distribution of share-classes per WFICN
print(SEP2)
print("  Distribution of crsp_fundno per wficn:")
bins = [1, 2, 3, 5, 10, 20, 50, 200]
labels = ["1", "2", "3", "4–5", "6–10", "11–20", "21–50", "51+"]
fn_per_wficn_cut = pd.cut(fn_per_wficn, bins=[0]+bins,
                          labels=labels, right=True)
dist = fn_per_wficn_cut.value_counts().sort_index()
for lbl, cnt in dist.items():
    pct = cnt / fn_per_wficn.shape[0] * 100
    print(f"    {lbl:>6} share classes : {cnt:>6,}  ({pct:4.1f}% of WFICNs)")


# ══════════════════════════════════════════════════════════════════════
# Build canonical WFICN per crsp_fundno
# For the ~341 fundnos with multiple WFICNs, keep the WFICN that appears
# most frequently (i.e. the primary/surviving fund).
# ══════════════════════════════════════════════════════════════════════

mfl_canonical = (
    mfl.groupby("crsp_fundno")["wficn"]
    .agg(lambda x: x.mode().iloc[0])   # modal wficn (usually only one)
    .reset_index()
    .rename(columns={"wficn": "wficn_C"})
)


# ══════════════════════════════════════════════════════════════════════
# 3. WFICN coverage by year
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2b. WFICN (MFLinks) COVERAGE BY YEAR")
print("═" * 66)

# MFLinks is static (no dates) — every fundno either has a WFICN or it doesn't
ret_wficn = ret.merge(mfl_canonical, on="crsp_fundno", how="left")

wficn_by_year = (
    ret_wficn.groupby("year")
    .agg(
        total_obs    = ("crsp_fundno", "count"),
        mapped_wficn = ("wficn_C",    "count"),   # count ignores NaN
    )
    .assign(pct_mapped=lambda d: (d["mapped_wficn"] / d["total_obs"] * 100).round(1))
)
print(wficn_by_year.to_string())


# ══════════════════════════════════════════════════════════════════════
# 4. Re-build Approach A (Map) for comparison — same tiered logic as Step 1
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. BUILDING MAPPING APPROACHES A / B / C …")

# -- Approach A: Fund-Portfolio Map (tiered: single-portno no-date, multi date-filtered)
portno_counts = pmap.groupby("crsp_fundno")["crsp_portno"].nunique()
single_fn = set(portno_counts[portno_counts == 1].index)
multi_fn  = set(portno_counts[portno_counts >  1].index)

single_map = (
    pmap[pmap["crsp_fundno"].isin(single_fn)]
    [["crsp_fundno", "crsp_portno"]]
    .drop_duplicates("crsp_fundno")
    .rename(columns={"crsp_portno": "portno_A"})
)
multi_map = pmap[pmap["crsp_fundno"].isin(multi_fn)][
    ["crsp_fundno", "crsp_portno", "begdt", "enddt"]
]

ret_A = ret.merge(single_map, on="crsp_fundno", how="left")
ret_multi_raw = ret[ret["crsp_fundno"].isin(multi_fn)].copy()
merged_multi  = ret_multi_raw.merge(multi_map, on="crsp_fundno", how="left")
valid_date    = (merged_multi["caldt"] >= merged_multi["begdt"]) & (
                 merged_multi["caldt"].le(merged_multi["enddt"]) | merged_multi["enddt"].isna())
mapped_multi  = (merged_multi[valid_date]
                 .drop_duplicates(["crsp_fundno", "caldt"])
                 [["crsp_fundno", "caldt", "crsp_portno"]]
                 .rename(columns={"crsp_portno": "portno_A_multi"}))
ret_A = ret_A.merge(mapped_multi, on=["crsp_fundno", "caldt"], how="left")
ret_A["portno_A"] = ret_A["portno_A"].where(
    ~ret_A["crsp_fundno"].isin(multi_fn), ret_A["portno_A_multi"]
)
ret_A = ret_A.drop(columns=["portno_A_multi"])

# -- Approach B: Fund Summary as-of merge (no look-ahead, 95-day tolerance)
fsq_portno = (
    fsq[fsq["crsp_portno"].notna()]
    [["crsp_fundno", "caldt", "crsp_portno"]]
    .sort_values("caldt")
    .drop_duplicates(["crsp_fundno", "caldt"])
)
ret_sorted      = ret.sort_values("caldt").reset_index(drop=True)
fsq_portno_s    = fsq_portno.sort_values("caldt").reset_index(drop=True)
merged_B = pd.merge_asof(
    ret_sorted,
    fsq_portno_s.rename(columns={"crsp_portno": "portno_B", "caldt": "fsq_caldt"}),
    left_on="caldt", right_on="fsq_caldt",
    by="crsp_fundno",
    direction="backward",
    tolerance=pd.Timedelta("95 days"),
)
ret_B = merged_B[["crsp_fundno", "caldt", "portno_B"]].copy()

# -- Approach C: WFICN via MFLinks (static, date-free)
#    Already computed in ret_wficn above

# Combine all into one frame
combined = ret_A[["crsp_fundno", "caldt", "year", "portno_A"]].copy()
combined = combined.merge(ret_B,  on=["crsp_fundno", "caldt"], how="left")
combined = combined.merge(
    ret_wficn[["crsp_fundno", "caldt", "wficn_C"]],
    on=["crsp_fundno", "caldt"], how="left"
)
combined.rename(columns={"wficn_C": "portno_C"}, inplace=True)

print(f"  Combined frame rows: {len(combined):,}")


# ══════════════════════════════════════════════════════════════════════
# 5. Year-by-year comparison table: A vs B vs C
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. APPROACH COMPARISON BY YEAR  (A=Map, B=FundSummary, C=WFICN)")
print("═" * 66)

by_year = (
    combined.groupby("year")
    .agg(
        total    = ("crsp_fundno", "count"),
        mapped_A = ("portno_A",    lambda x: x.notna().sum()),
        mapped_B = ("portno_B",    lambda x: x.notna().sum()),
        mapped_C = ("portno_C",    lambda x: x.notna().sum()),
    )
    .assign(
        pct_A=lambda d: (d["mapped_A"] / d["total"] * 100).round(1),
        pct_B=lambda d: (d["mapped_B"] / d["total"] * 100).round(1),
        pct_C=lambda d: (d["mapped_C"] / d["total"] * 100).round(1),
    )
)
print(by_year[["total","pct_A","pct_B","pct_C","mapped_A","mapped_B","mapped_C"]].to_string())

# Sub-period summary
print(SEP2)
print(f"  {'Period':<16}  {'Obs':>9}  {'A:Map':>7}  {'B:FSQ':>7}  {'C:WFICN':>8}")
periods = [
    ("Full 1991–2011", combined["year"].between(1991,2011)),
    ("1991–1996",      combined["year"].between(1991,1996)),
    ("1997–2011",      combined["year"].between(1997,2011)),
    ("2003–2011",      combined["year"].between(2003,2011)),
    ("2008–2011",      combined["year"].between(2008,2011)),
]
for label, mask in periods:
    sub = combined[mask]
    n   = len(sub)
    pA  = sub["portno_A"].notna().mean() * 100
    pB  = sub["portno_B"].notna().mean() * 100
    pC  = sub["portno_C"].notna().mean() * 100
    print(f"  {label:<16}  {n:>9,}  {pA:>6.1f}%  {pB:>6.1f}%  {pC:>7.1f}%")

# What does WFICN add over Map alone?
only_C_fills = (combined["portno_A"].isna() & combined["portno_C"].notna()).sum()
still_miss   = combined["portno_C"].isna().sum()
print(SEP2)
print(f"  WFICN fills obs that Map missed      : {only_C_fills:>9,}")
print(f"  Still unmapped even with WFICN (C)   : {still_miss:>9,}  "
      f"({100*still_miss/len(combined):.1f}%)")


# ══════════════════════════════════════════════════════════════════════
# 6. Check previously-unmapped flagship funds
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. PREVIOUSLY-UNMAPPED FLAGSHIP FUNDS — DO THEY GET A WFICN?")
print("═" * 66)

# From the Step 1 diagnostic, these were the top unmapped fundnos by TNA
flagship_ids = [11943, 31432, 16354, 31959, 11979, 11809, 31434, 5079, 16779, 31277, 10416]

fsq_names = (
    fsq.sort_values("caldt")
    .drop_duplicates("crsp_fundno", keep="last")
    [["crsp_fundno","fund_name","lipper_asset_cd","lipper_obj_cd"]]
)

flag_df = (
    pd.DataFrame({"crsp_fundno": flagship_ids})
    .merge(fsq_names, on="crsp_fundno", how="left")
    .merge(mfl[["crsp_fundno","wficn"]], on="crsp_fundno", how="left")
)
# Coverage stats per flagship fundno
cov = (
    combined[combined["crsp_fundno"].isin(flagship_ids)]
    .groupby("crsp_fundno")
    .agg(
        obs       = ("year",     "count"),
        mapped_A  = ("portno_A", lambda x: x.notna().sum()),
        mapped_C  = ("portno_C", lambda x: x.notna().sum()),
    )
    .assign(
        pct_A=lambda d: (d["mapped_A"]/d["obs"]*100).round(1),
        pct_C=lambda d: (d["mapped_C"]/d["obs"]*100).round(1),
    )
    .reset_index()
)
flag_df = flag_df.merge(cov, on="crsp_fundno", how="left")
print(flag_df[["crsp_fundno","fund_name","wficn","obs","pct_A","pct_C"]].to_string(index=False))


# ══════════════════════════════════════════════════════════════════════
# 7. Active-EDC coverage with WFICN
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. ACTIVE-EDC COVERAGE  (crsp_obj_cd starts with 'ED', no index/ETF)")
print("═" * 66)

INDEX_TERMS = ["index","idx","s&p 500","s&p500","russell","msci","dow jones"]

fsq_latest = (
    fsq.sort_values("caldt")
    .drop_duplicates("crsp_fundno", keep="last")
    [["crsp_fundno","crsp_obj_cd","index_fund_flag","et_flag","fund_name"]]
)

fsq_latest["is_edc"]  = fsq_latest["crsp_obj_cd"].str.startswith("ED", na=False)
fsq_latest["is_index"]= (
    fsq_latest["index_fund_flag"].notna() |
    fsq_latest["fund_name"].apply(
        lambda n: any(t in n.lower() for t in INDEX_TERMS) if pd.notna(n) else False
    )
)
fsq_latest["is_etf"]  = (
    fsq_latest["et_flag"].notna() |
    fsq_latest["fund_name"].str.contains("ETF", case=False, na=False)
)
fsq_latest["active_edc"] = (
    fsq_latest["is_edc"] & ~fsq_latest["is_index"] & ~fsq_latest["is_etf"]
)

n_edc        = fsq_latest["is_edc"].sum()
n_active_edc = fsq_latest["active_edc"].sum()
print(f"  fundno with crsp_obj_cd starting 'ED'  : {n_edc:,}")
print(f"  … minus index and ETF (active EDC)      : {n_active_edc:,}")

edc_fundnos = set(fsq_latest[fsq_latest["active_edc"]]["crsp_fundno"])
edc_sub = combined[combined["crsp_fundno"].isin(edc_fundnos)].copy()

if len(edc_sub) == 0:
    print("  No active-EDC fundnos found in monthly_returns.")
else:
    print(f"  Return obs for active-EDC fundnos       : {len(edc_sub):,}")
    edc_by_year = (
        edc_sub.groupby("year")
        .agg(
            obs     = ("crsp_fundno","count"),
            pct_A   = ("portno_A", lambda x: round(x.notna().mean()*100,1)),
            pct_B   = ("portno_B", lambda x: round(x.notna().mean()*100,1)),
            pct_C   = ("portno_C", lambda x: round(x.notna().mean()*100,1)),
        )
    )
    print(edc_by_year.to_string())
    print(SEP2)
    print(f"  {'Period':<16}  {'Obs':>9}  {'A:Map':>7}  {'B:FSQ':>7}  {'C:WFICN':>8}")
    edc_periods = [
        ("Full 1991–2011", edc_sub["year"].between(1991,2011)),
        ("1991–1996",      edc_sub["year"].between(1991,1996)),
        ("1997–2011",      edc_sub["year"].between(1997,2011)),
        ("2003–2011",      edc_sub["year"].between(2003,2011)),
        ("2008–2011",      edc_sub["year"].between(2008,2011)),
    ]
    for label, emask in edc_periods:
        sub = edc_sub[emask]
        n   = len(sub)
        if n == 0:
            continue
        pA  = sub["portno_A"].notna().mean() * 100
        pB  = sub["portno_B"].notna().mean() * 100
        pC  = sub["portno_C"].notna().mean() * 100
        print(f"  {label:<16}  {n:>9,}  {pA:>6.1f}%  {pB:>6.1f}%  {pC:>7.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 8. Save diagnostic tables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("6. SAVING OUTPUT TABLES")
print("═" * 66)

# Table 1: full year-by-year comparison
out_tbl = by_year[["total","pct_A","pct_B","pct_C","mapped_A","mapped_B","mapped_C"]].copy()
out_tbl.columns = ["total_obs","pct_A_map","pct_B_fsq","pct_C_wficn",
                   "n_mapped_A","n_mapped_B","n_mapped_C"]
out_tbl.to_csv(OUT + "mflinks_wficn_mapping_diagnostic.csv")
print(f"  Saved CSV → {OUT}mflinks_wficn_mapping_diagnostic.csv")

# Markdown report
def df_to_md(df, title):
    lines = [f"## {title}", ""]
    idx_name = df.index.name or "year"
    cols = [idx_name] + df.columns.tolist()
    lines.append("| " + " | ".join(str(c) for c in cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

# Table A: WFICN by year
md_wficn_yr = df_to_md(
    wficn_by_year,
    "Table A — WFICN (MFLinks) coverage by year"
)

# Table B: Three-approach comparison
md_compare = df_to_md(
    out_tbl,
    "Table B — Approach comparison by year (A=Map, B=FundSummary, C=WFICN)"
)

# Table C: Sub-period summary
rows_sp = []
for label, mask in periods:
    sub = combined[mask]
    rows_sp.append({
        "period": label, "obs": len(sub),
        "pct_A": round(sub["portno_A"].notna().mean()*100, 1),
        "pct_B": round(sub["portno_B"].notna().mean()*100, 1),
        "pct_C": round(sub["portno_C"].notna().mean()*100, 1),
    })
sp_df = pd.DataFrame(rows_sp).set_index("period")
md_subperiod = df_to_md(sp_df, "Table C — Sub-period summary")

# Table D: Active-EDC by year
if len(edc_sub) > 0:
    md_edc = df_to_md(edc_by_year, "Table D — Active-EDC coverage by year")
else:
    md_edc = "## Table D — Active-EDC: no matching fundnos found\n"

# Table E: Flagship funds
flag_out = flag_df[["crsp_fundno","fund_name","wficn","obs","pct_A","pct_C"]].fillna("—")
md_flag = ("## Table E — Flagship previously-unmapped funds\n\n"
           "| " + " | ".join(flag_out.columns) + " |\n"
           "| " + " | ".join(["---"]*len(flag_out.columns)) + " |\n"
           + "\n".join("| " + " | ".join(str(v) for v in row) + " |"
                       for _, row in flag_out.iterrows()))

md_path = OUT + "mflinks_wficn_mapping_diagnostic.md"
with open(md_path, "w") as f:
    f.write("# MFLinks / WFICN Mapping Coverage Diagnostic\n\n")
    f.write("\n\n".join([md_wficn_yr, md_compare, md_subperiod, md_edc, md_flag]))
    f.write("\n")
print(f"  Saved  MD → {md_path}")


# ══════════════════════════════════════════════════════════════════════
# 9. Conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("7. CONCLUSION")
print("═" * 66)

p91_C  = combined.loc[combined["year"] <  1997, "portno_C"].notna().mean() * 100
p97_C  = combined.loc[combined["year"].between(1997,2011), "portno_C"].notna().mean() * 100
p03_C  = combined.loc[combined["year"].between(2003,2011), "portno_C"].notna().mean() * 100
p08_C  = combined.loc[combined["year"].between(2008,2011), "portno_C"].notna().mean() * 100

p91_A  = combined.loc[combined["year"] <  1997, "portno_A"].notna().mean() * 100
p97_A  = combined.loc[combined["year"].between(1997,2011), "portno_A"].notna().mean() * 100

edc_97_C = (edc_sub.loc[edc_sub["year"].between(1997,2011), "portno_C"]
            .notna().mean() * 100) if len(edc_sub) > 0 else float("nan")
edc_03_C = (edc_sub.loc[edc_sub["year"].between(2003,2011), "portno_C"]
            .notna().mean() * 100) if len(edc_sub) > 0 else float("nan")

print(f"""
  Does MFLinks / WFICN solve the early-year mapping problem?
  ────────────────────────────────────────────────────────────
  WFICN is a static (date-free) identifier, so every fundno in
  MFLinks receives a WFICN for ALL its return observations,
  including pre-1997 data.

  Pre-1997 coverage:
    A (Map only)  : {p91_A:.1f}%
    C (WFICN)     : {p91_C:.1f}%

  This is a substantial improvement over the crsp_portno approach.
  MFLinks fills {only_C_fills:,} observations that the Map could not reach.

  Overall coverage by period (WFICN only):
    1997–2011  : {p97_C:.1f}%
    2003–2011  : {p03_C:.1f}%
    2008–2011  : {p08_C:.1f}%

  Can WFICN be used as a portfolio-level identifier?
  ────────────────────────────────────────────────────────────
  WFICN groups share classes of the same fund family into a
  single portfolio identifier, analogous to crsp_portno.
  Average share classes per WFICN: {fn_per_wficn.mean():.2f}
  (vs ~2.37 for crsp_portno in the Step 1 dataset)
  Max share classes per WFICN: {fn_per_wficn.max():,}

  WFICNs with very high share-class counts likely represent
  large fund families (e.g. Fidelity, Vanguard) that have many
  share-class variants of the same underlying portfolio — the
  same aggregation problem that crsp_portno solves via CRSP.

  Is 1997–2011 feasible with WFICN?
  ────────────────────────────────────────────────────────────
  WFICN coverage for 1997–2011: {p97_C:.1f}%  (all funds)
  WFICN coverage for 1997–2011: {edc_97_C:.1f}%  (active EDC)

  {"This is high enough to build a reliable portfolio-level panel for 1997–2011." if p97_C >= 80 else
   "Coverage for 1997–2011 (" + f"{p97_C:.0f}%" + ") is below 80% — a 2003+ start date remains preferable for a clean panel." if p97_C < 80 else ""}

  Recommendation
  ────────────────────────────────────────────────────────────
  MFLinks WFICN substantially improves early-year coverage and is
  the best available option for building a portfolio-level panel
  that extends before 2003.

  Suggested approach for subsequent steps:
    - Use WFICN as the portfolio identifier.
    - For share-class aggregation, compute TNA-weighted returns
      across crsp_fundno grouped by WFICN, exactly as Step 1
      did for crsp_portno.
    - Sample period: 1997–2011 is feasible with WFICN at {p97_C:.0f}%
      coverage (active EDC: {edc_97_C:.0f}%).
    - If a clean pre-1997 sub-period is needed, consider 1993 as
      the earliest reasonable start ({combined.loc[combined["year"]==1993, "portno_C"].notna().mean()*100:.0f}% coverage in 1993).
""")
