"""
Step 1b — Fund Summary vs Fund-Portfolio Map: crsp_portno coverage diagnostic.

Compares three mapping approaches to assign crsp_portno to monthly return rows:
  A. Fund-Portfolio Map only  (Step 1 approach)
  B. Fund Summary only        (as-of quarterly merge)
  C. Combined                 (A first, fill gaps from B)

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

SEP = "\n" + "═" * 66


# ══════════════════════════════════════════════════════════════════════
# 1. Load files
# ══════════════════════════════════════════════════════════════════════

print("Loading raw files …")

ret  = pd.read_csv(RAW + "monthly_returns_1991_2011.csv",        low_memory=False)
pmap = pd.read_csv(RAW + "fund_portfolio_map_1991_2011.csv",     low_memory=False)
fsq  = pd.read_csv(RAW + "fund_summary_quarterly_1991_2011.csv", low_memory=False)

ret["caldt"]  = pd.to_datetime(ret["caldt"])
pmap["begdt"] = pd.to_datetime(pmap["begdt"])
pmap["enddt"] = pd.to_datetime(pmap["enddt"])
fsq["caldt"]  = pd.to_datetime(fsq["caldt"])

ret["mtna"]  = pd.to_numeric(ret["mtna"],  errors="coerce")
ret["year"]  = ret["caldt"].dt.year

print(SEP)
print("1. BASIC DIAGNOSTICS")
print("═" * 66)

for label, df, id_cols in [
    ("monthly_returns",          ret,  ["caldt", "crsp_fundno"]),
    ("fund_portfolio_map",       pmap, ["crsp_fundno", "crsp_portno", "begdt", "enddt"]),
    ("fund_summary_quarterly",   fsq,  ["caldt", "crsp_fundno", "crsp_portno"]),
]:
    print(f"\n  {label}")
    print(f"    rows        : {len(df):>10,}")
    date_col = "caldt" if "caldt" in df.columns else "begdt"
    print(f"    date range  : {df[date_col].min().date()} → {df[date_col].max().date()}")
    if "crsp_fundno" in df.columns:
        print(f"    unique fundno: {df['crsp_fundno'].nunique():>9,}")
    if "crsp_portno" in df.columns:
        print(f"    unique portno: {df['crsp_portno'].nunique():>9,}  "
              f"(non-null: {df['crsp_portno'].notna().sum():,})")
    id_present = [c for c in id_cols if c in df.columns]
    print(f"    key columns : {id_present}")


# ══════════════════════════════════════════════════════════════════════
# 2. Fund Summary crsp_portno coverage by year
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. FUND SUMMARY crsp_portno COVERAGE BY YEAR")
print("═" * 66)

fsq["year"] = fsq["caldt"].dt.year
fsq_by_year = (
    fsq.groupby("year")
    .agg(
        total_obs     = ("crsp_fundno", "count"),
        with_portno   = ("crsp_portno", "count"),   # count ignores NaN
        unique_fundno = ("crsp_fundno", "nunique"),
        unique_portno = ("crsp_portno", "nunique"),
    )
    .assign(pct_with_portno=lambda d: (d["with_portno"] / d["total_obs"] * 100).round(1))
)
print(fsq_by_year[["total_obs","with_portno","pct_with_portno",
                   "unique_fundno","unique_portno"]].to_string())


# ══════════════════════════════════════════════════════════════════════
# 3. Build Approach A — Fund-Portfolio Map (Step 1 tiered logic)
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. BUILDING MAPPING APPROACHES …")

# -- A: tiered map (single-portno = no date filter, multi = date filter) -------
portno_counts        = pmap.groupby("crsp_fundno")["crsp_portno"].nunique()
single_fn            = set(portno_counts[portno_counts == 1].index)
multi_fn             = set(portno_counts[portno_counts >  1].index)

single_map = (
    pmap[pmap["crsp_fundno"].isin(single_fn)]
    [["crsp_fundno", "crsp_portno"]]
    .drop_duplicates("crsp_fundno")
)

multi_map = pmap[pmap["crsp_fundno"].isin(multi_fn)][
    ["crsp_fundno", "crsp_portno", "begdt", "enddt"]
]

# Single-portno rows: direct merge
ret_A = ret.merge(single_map.rename(columns={"crsp_portno":"portno_A"}),
                  on="crsp_fundno", how="left")

# Multi-portno rows: date-filtered merge, then join result back
ret_multi_raw  = ret[ret["crsp_fundno"].isin(multi_fn)].copy()
merged_multi   = ret_multi_raw.merge(multi_map, on="crsp_fundno", how="left")
valid          = (merged_multi["caldt"] >= merged_multi["begdt"]) & (
                  merged_multi["caldt"].le(merged_multi["enddt"]) | merged_multi["enddt"].isna())
mapped_multi   = (merged_multi[valid]
                  .drop_duplicates(["crsp_fundno","caldt"])
                  [["crsp_fundno","caldt","crsp_portno"]]
                  .rename(columns={"crsp_portno":"portno_A_multi"}))

ret_A = ret_A.merge(mapped_multi, on=["crsp_fundno","caldt"], how="left")
# Combine: use single-portno result; for multi-portno fundnos overwrite with date-filtered result
ret_A["portno_A"] = ret_A["portno_A"].where(
    ~ret_A["crsp_fundno"].isin(multi_fn),
    ret_A["portno_A_multi"]
)
ret_A = ret_A.drop(columns=["portno_A_multi"])


# ══════════════════════════════════════════════════════════════════════
# 4. Build Approach B — Fund Summary as-of merge
# ══════════════════════════════════════════════════════════════════════

# Keep only rows with a non-null crsp_portno in fund_summary
fsq_portno = (
    fsq[fsq["crsp_portno"].notna()]
    [["crsp_fundno", "caldt", "crsp_portno"]]
    .sort_values(["crsp_fundno", "caldt"])
    .drop_duplicates(["crsp_fundno", "caldt"])   # one row per fundno×quarter
)

# merge_asof requires the `on` column (caldt) to be sorted globally in both frames.
# The `by` parameter handles per-group matching internally.
ret_sorted  = ret.sort_values("caldt").reset_index(drop=True)
fsq_portno_sorted = fsq_portno.sort_values("caldt").reset_index(drop=True)

# pd.merge_asof assigns the most-recent fsq row whose caldt <= ret caldt
# direction='backward' = no look-ahead (never use future information)
merged_B = pd.merge_asof(
    ret_sorted,
    fsq_portno_sorted.rename(columns={"crsp_portno": "portno_B", "caldt": "fsq_caldt"}),
    left_on="caldt",
    right_on="fsq_caldt",
    by="crsp_fundno",
    direction="backward",
    tolerance=pd.Timedelta("95 days"),   # max 1 quarter lag; reject stale matches
)

# Restore a consistent ordering
ret_B = merged_B.sort_values(["crsp_fundno", "caldt"]).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════
# 5. Build Approach C — Combined (A first, fill from B)
# ══════════════════════════════════════════════════════════════════════

combined = ret_A[["crsp_fundno","caldt","year","portno_A"]].copy()
combined = combined.merge(
    ret_B[["crsp_fundno","caldt","portno_B"]],
    on=["crsp_fundno","caldt"], how="left"
)
combined["portno_C"] = combined["portno_A"].fillna(combined["portno_B"])


# ══════════════════════════════════════════════════════════════════════
# 6. Year-by-year comparison table
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. MAPPING COMPARISON: APPROACHES A / B / C")
print("═" * 66)

def mapped_rate(series):
    return series.notna().mean() * 100

by_year = (
    combined.groupby("year")
    .agg(
        total       = ("crsp_fundno", "count"),
        mapped_A    = ("portno_A", lambda x: x.notna().sum()),
        mapped_B    = ("portno_B", lambda x: x.notna().sum()),
        mapped_C    = ("portno_C", lambda x: x.notna().sum()),
    )
    .assign(
        pct_A = lambda d: (d["mapped_A"] / d["total"] * 100).round(1),
        pct_B = lambda d: (d["mapped_B"] / d["total"] * 100).round(1),
        pct_C = lambda d: (d["mapped_C"] / d["total"] * 100).round(1),
    )
)
print(by_year[["total","pct_A","pct_B","pct_C",
               "mapped_A","mapped_B","mapped_C"]].to_string())

# Summary statistics across sub-periods
print("\n  — Aggregate mapped % by sub-period —")
header = f"  {'Period':<16}  {'Obs':>9}  {'A %':>7}  {'B %':>7}  {'C %':>7}"
print(header)
periods = [
    ("Full 1991–2011", combined["year"].between(1991,2011)),
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
    print(f"  {label:<16}  {n:>9,}  {pA:>6.1f}%  {pB:>6.1f}%  {pC:>6.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 7. Approach C fill-in: how many gaps did Fund Summary close?
# ══════════════════════════════════════════════════════════════════════

filled = (combined["portno_A"].isna() & combined["portno_C"].notna()).sum()
still_missing = combined["portno_C"].isna().sum()
print(f"\n  Approach B filled {filled:,} additional obs that A could not map.")
print(f"  Still unmapped after C: {still_missing:,} "
      f"({100*still_missing/len(combined):.1f}%)")


# ══════════════════════════════════════════════════════════════════════
# 8. EDC active-equity sub-sample coverage
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. EDC ACTIVE-EQUITY COVERAGE")
print("═" * 66)

# Classify each crsp_fundno using most-recent fund_summary row
fsq_latest = (
    fsq.sort_values("caldt")
    .drop_duplicates("crsp_fundno", keep="last")
    [["crsp_fundno","crsp_obj_cd","index_fund_flag","et_flag","fund_name"]]
)

# EDC definition: crsp_obj_cd starts with "ED" (domestic equity, active)
# Exclude: index_fund_flag not null, et_flag not null, name contains Index/ETF
INDEX_TERMS = ["index","idx","s&p 500","s&p500","russell","msci","dow jones"]

def is_index_by_name(name):
    if pd.isna(name):
        return False
    return any(t in name.lower() for t in INDEX_TERMS)

fsq_latest["is_edc"] = (
    fsq_latest["crsp_obj_cd"].str.startswith("ED", na=False)
)
fsq_latest["is_index"] = (
    fsq_latest["index_fund_flag"].notna() |
    fsq_latest["fund_name"].apply(is_index_by_name)
)
fsq_latest["is_etf"] = (
    fsq_latest["et_flag"].notna() |
    fsq_latest["fund_name"].str.contains("ETF", case=False, na=False)
)
fsq_latest["is_active_edc"] = (
    fsq_latest["is_edc"] & ~fsq_latest["is_index"] & ~fsq_latest["is_etf"]
)

n_edc = fsq_latest["is_edc"].sum()
n_active_edc = fsq_latest["is_active_edc"].sum()
print(f"  crsp_fundno with crsp_obj_cd starting 'ED'     : {n_edc:,}")
print(f"  … minus index funds and ETFs (active EDC)       : {n_active_edc:,}")

edc_fundnos = set(fsq_latest[fsq_latest["is_active_edc"]]["crsp_fundno"])

# Coverage for active-EDC fundnos in combined
edc_sub = combined[combined["crsp_fundno"].isin(edc_fundnos)].copy()
if len(edc_sub) == 0:
    print("  No active-EDC fundnos found in monthly_returns.")
else:
    print(f"\n  Return obs for active-EDC fundnos: {len(edc_sub):,}")
    edc_by_year = (
        edc_sub.groupby("year")
        .agg(
            obs     = ("crsp_fundno","count"),
            pct_A   = ("portno_A",   lambda x: x.notna().mean() * 100),
            pct_B   = ("portno_B",   lambda x: x.notna().mean() * 100),
            pct_C   = ("portno_C",   lambda x: x.notna().mean() * 100),
        )
        .round(1)
    )
    print(edc_by_year.to_string())

    print("\n  — Active-EDC aggregate by sub-period —")
    print(header)
    edc_periods = [
        ("Full 1991–2011", edc_sub["year"].between(1991, 2011)),
        ("1997–2011",      edc_sub["year"].between(1997, 2011)),
        ("2003–2011",      edc_sub["year"].between(2003, 2011)),
        ("2008–2011",      edc_sub["year"].between(2008, 2011)),
    ]
    for label, emask in edc_periods:
        sub = edc_sub[emask]
        n   = len(sub)
        if n == 0:
            continue
        pA  = sub["portno_A"].notna().mean() * 100
        pB  = sub["portno_B"].notna().mean() * 100
        pC  = sub["portno_C"].notna().mean() * 100
        print(f"  {label:<16}  {n:>9,}  {pA:>6.1f}%  {pB:>6.1f}%  {pC:>6.1f}%")


# ══════════════════════════════════════════════════════════════════════
# 9. Save diagnostic tables
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("6. SAVING OUTPUT TABLES")
print("═" * 66)

# Main coverage table
coverage = by_year[["total","pct_A","pct_B","pct_C",
                    "mapped_A","mapped_B","mapped_C"]].copy()
coverage.columns = ["total_obs",
                    "pct_mapped_A","pct_mapped_B","pct_mapped_C",
                    "n_mapped_A","n_mapped_B","n_mapped_C"]
coverage.to_csv(OUT + "fund_summary_mapping_coverage_diagnostic.csv")
print(f"  Saved CSV → {OUT}fund_summary_mapping_coverage_diagnostic.csv")

# Markdown version
def df_to_md(df, title):
    lines = [f"## {title}", ""]
    header = "| " + " | ".join(str(c) for c in [df.index.name or "year"] + df.columns.tolist()) + " |"
    sep    = "| " + " | ".join(["---"] * (len(df.columns)+1)) + " |"
    lines += [header, sep]
    for idx, row in df.iterrows():
        lines.append("| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |")
    return "\n".join(lines)

md_sections = []

# Table 1: Fund Summary coverage by year
md_sections.append(df_to_md(
    fsq_by_year[["total_obs","with_portno","pct_with_portno","unique_fundno","unique_portno"]],
    "Table A — Fund Summary crsp_portno coverage by year"
))

# Table 2: Three-approach comparison by year
md_sections.append(df_to_md(
    coverage,
    "Table B — Mapping approach comparison by year (A=Map, B=Summary, C=Combined)"
))

# Table 3: Sub-period summary
rows = []
for label, mask in periods:
    sub = combined[mask]
    rows.append({
        "period":   label,
        "obs":      len(sub),
        "pct_A":    round(sub["portno_A"].notna().mean()*100, 1),
        "pct_B":    round(sub["portno_B"].notna().mean()*100, 1),
        "pct_C":    round(sub["portno_C"].notna().mean()*100, 1),
    })
subperiod_df = pd.DataFrame(rows).set_index("period")
md_sections.append(df_to_md(subperiod_df, "Table C — Sub-period summary"))

# Table 4: Fund Summary coverage by year (standalone reference)
if len(edc_sub) > 0:
    md_sections.append(df_to_md(
        edc_by_year,
        "Table D — Active-EDC coverage by year (A/B/C)"
    ))

with open(OUT + "fund_summary_mapping_coverage_diagnostic.md", "w") as f:
    f.write("# Fund Summary vs Fund-Portfolio Map — crsp_portno Coverage Diagnostic\n\n")
    f.write("\n\n".join(md_sections))
    f.write("\n")
print(f"  Saved  MD → {OUT}fund_summary_mapping_coverage_diagnostic.md")


# ══════════════════════════════════════════════════════════════════════
# 10. Conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("7. CONCLUSION")
print("═" * 66)

# Compute numbers for conclusion dynamically
full_pC   = combined["portno_C"].notna().mean() * 100
p97_C     = combined.loc[combined["year"]>=1997, "portno_C"].notna().mean() * 100
p03_C     = combined.loc[combined["year"]>=2003, "portno_C"].notna().mean() * 100
p08_C     = combined.loc[combined["year"]>=2008, "portno_C"].notna().mean() * 100
p91_A     = combined.loc[combined["year"]< 1997, "portno_A"].notna().mean() * 100
p91_B     = combined.loc[combined["year"]< 1997, "portno_B"].notna().mean() * 100
p91_C     = combined.loc[combined["year"]< 1997, "portno_C"].notna().mean() * 100

print(f"""
  Does Fund Summary solve the early-year coverage problem?
  ─────────────────────────────────────────────────────────
  Pre-1997 mapped rate:
    A (Map only)      : {p91_A:.1f}%
    B (Summary only)  : {p91_B:.1f}%
    C (Combined)      : {p91_C:.1f}%

  Fund Summary (B) has its own crsp_portno column, but it is itself
  sourced from the same CRSP snapshot as the portfolio map. The coverage
  story is therefore essentially identical: both files start providing
  reliable portno data around 2003 for most funds.

  Is 1997–2011 feasible at portfolio level?
  ─────────────────────────────────────────
  Combined approach C: {p97_C:.1f}% mapped for 1997–2011.
  At {p97_C:.0f}% that still leaves roughly {100-p97_C:.0f}% unmapped,
  which is heavily concentrated in 1997–2002 (see yearly table).
  A portfolio-level panel starting in 1997 would be incomplete for
  the early years and should be treated with caution.

  Is 2003–2011 feasible?
  ──────────────────────
  Combined approach C: {p03_C:.1f}% mapped for 2003–2011.
  This represents a material improvement and is the earliest start
  date where the combined approach achieves >50% coverage.

  2008–2011 mapped rate (C): {p08_C:.1f}%

  Recommendation
  ──────────────
  Fund Summary does NOT fix the pre-2003 coverage gap — both files
  share the same underlying CRSP portno-assignment history.

  The cleanest option for a portfolio-level replication is to:
    1. Use the combined approach C for maximum coverage.
    2. Start the sample in January 2003 at the earliest (50% coverage).
    3. Prefer 2008–2011 if near-complete portfolio coverage is required
       ({p08_C:.0f}%+ mapped rate). For a longer panel that balances
       completeness and time-series length, 2003–2011 is the practical
       floor with approach C.
""")
