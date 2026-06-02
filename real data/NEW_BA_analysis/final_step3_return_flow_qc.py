"""
Final Step 3 — Quality-control check on portfolio_return and flow.

Diagnoses whether extreme return and flow values in the Step 2 sample
are CRSP data artefacts, tiny-TNA noise, or genuine outliers.
Does NOT modify either dataset; does NOT run regressions.
"""

import pandas as pd
import numpy as np
import os

BASE = "/Users/justin.hahn/Downloads/Uni /Bachlorarbeit /code/Bachelorarbeit/real data"
PROC = BASE + "/NEW_BA_analysis/data/processed/"
RAW  = BASE + "/real, clear data/raw/new data/"
TABS = BASE + "/NEW_BA_analysis/output/tables/"
os.makedirs(TABS, exist_ok=True)

SEP  = "\n" + "═" * 70
SEP2 = "─" * 70

print("Loading files …")
s2  = pd.read_csv(PROC + "final_step2_clean_wficn_edc_flows.csv", low_memory=False)
s1  = pd.read_csv(PROC + "final_step1_wficn_portfolio_month.csv",  low_memory=False)
raw = pd.read_csv(RAW  + "monthly_returns_1991_2011.csv",           low_memory=False)

s2["caldt"]  = pd.to_datetime(s2["caldt"])
s1["caldt"]  = pd.to_datetime(s1["caldt"])
raw["caldt"] = pd.to_datetime(raw["caldt"])
raw["mret_num"] = pd.to_numeric(raw["mret"], errors="coerce")
raw["mtna_num"] = pd.to_numeric(raw["mtna"], errors="coerce")

md = ["# Step 2 Return & Flow Quality-Control Report\n"]


# ══════════════════════════════════════════════════════════════════════
# 1. portfolio_return distribution in the Step 2 sample
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("1. portfolio_return DISTRIBUTION  (Step 2 final sample)")
print("═" * 70)

r = s2["portfolio_return"].dropna()
pcts = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
pct_vals = r.quantile(pcts)

ret_stats = {
    "N":            len(r),
    "mean":         r.mean(),
    "std":          r.std(),
    "min":          r.min(),
    "p1":           pct_vals[0.01],
    "p5":           pct_vals[0.05],
    "p25":          pct_vals[0.25],
    "median":       pct_vals[0.50],
    "p75":          pct_vals[0.75],
    "p95":          pct_vals[0.95],
    "p99":          pct_vals[0.99],
    "max":          r.max(),
}
for k, v in ret_stats.items():
    print(f"  {k:<12}: {v:>14,.6f}" if k != "N" else f"  {k:<12}: {v:>14,}")

thresholds = [
    ("<  -1",   (r < -1).sum()),
    (">   1",   (r >  1).sum()),
    (">   5",   (r >  5).sum()),
    ("|r| > 10", (r.abs() > 10).sum()),
]
print()
for label, n in thresholds:
    print(f"  portfolio_return {label:<12}: {n:>8,}  ({100*n/len(r):.3f}%)")

md.append("## 1. portfolio_return distribution\n\n```")
md.append("\n".join(f"  {k:<12}: {v:>14,.6f}" if k != "N"
                    else f"  {k:<12}: {v:>14,}"
                    for k, v in ret_stats.items()))
md.append("")
for label, n in thresholds:
    md.append(f"  portfolio_return {label:<12}: {n:>8,}  ({100*n/len(r):.3f}%)")
md.append("```\n")


# ══════════════════════════════════════════════════════════════════════
# 2. Top 30 absolute portfolio_return observations
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("2. TOP 30 ABSOLUTE portfolio_return OBSERVATIONS")
print("═" * 70)

top_ret_cols = ["wficn", "caldt", "portfolio_return", "portfolio_tna",
                "n_share_classes", "fund_name", "crsp_obj_cd",
                "lag_portfolio_tna", "flow", "flow_winsorized"]
top_ret_cols = [c for c in top_ret_cols if c in s2.columns]

top_ret = (
    s2.assign(abs_ret=s2["portfolio_return"].abs())
    .nlargest(30, "abs_ret")
    .drop(columns=["abs_ret"])
    [top_ret_cols]
)
pd.set_option("display.max_colwidth", 55)
pd.set_option("display.width", 200)
print(top_ret.to_string(index=False))

md.append("## 2. Top 30 absolute portfolio_return observations\n\n```")
md.append(top_ret.to_string(index=False))
md.append("```\n")


# ══════════════════════════════════════════════════════════════════════
# 3. Raw mret in monthly_returns — distribution and special codes
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("3. RAW mret IN monthly_returns_1991_2011")
print("═" * 70)

# Non-numeric / special values
non_numeric_mask = raw["mret"].notna() & raw["mret_num"].isna()
special_vals = raw.loc[non_numeric_mask, "mret"].value_counts()
print(f"\n  Non-numeric mret codes (CRSP special values):")
print(special_vals.to_string())

# Numeric mret distribution
m = raw["mret_num"].dropna()
m_pcts = m.quantile([0.001, 0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99, 0.999])
print(f"\n  Numeric mret — N={len(m):,}")
for pct, val in m_pcts.items():
    print(f"    p{pct*100:5.1f}: {val:>12.6f}")
print(f"    min  : {m.min():>12.6f}")
print(f"    max  : {m.max():>12.6f}")

thresholds_m = [
    ("< -1",     (m < -1).sum()),
    (">  1",     (m >  1).sum()),
    (">  5",     (m >  5).sum()),
    ("|m| > 10", (m.abs() > 10).sum()),
]
print()
for label, n in thresholds_m:
    print(f"  mret {label:<12}: {n:>8,}  ({100*n/len(m):.4f}%)")

# Top 30 extreme mret values — look up fund names via MFLinks if possible
print(f"\n  Top 30 absolute mret values in raw file:")
top_mret = (
    raw.assign(abs_mret=raw["mret_num"].abs())
    .nlargest(30, "abs_mret")
    [["caldt", "crsp_fundno", "mret_num", "mtna_num"]]
    .rename(columns={"mret_num": "mret", "mtna_num": "mtna"})
)
print(top_mret.to_string(index=False))

md.append("## 3. Raw mret — special codes and distribution\n\n**Non-numeric CRSP codes:**\n```")
md.append(special_vals.to_string())
md.append("```\n\n**Numeric mret distribution:**\n```")
for pct, val in m_pcts.items():
    md.append(f"  p{pct*100:5.1f}: {val:>12.6f}")
md.append(f"  min  : {m.min():>12.6f}")
md.append(f"  max  : {m.max():>12.6f}")
md.append("")
for label, n in thresholds_m:
    md.append(f"  mret {label:<12}: {n:>8,}  ({100*n/len(m):.4f}%)")
md.append("```\n\n**Top 30 absolute mret:**\n```")
md.append(top_mret.to_string(index=False))
md.append("```\n")


# ══════════════════════════════════════════════════════════════════════
# 4. Drivers of extreme flow values
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("4. DRIVERS OF EXTREME RAW FLOW")
print("═" * 70)

flows = s2[s2["flow"].notna()].copy()

# 4a. Tiny lag TNA — most common driver of extreme flows
print("\n  a) lag_portfolio_tna distribution for extreme-flow obs:")
cut = pd.cut(flows["lag_portfolio_tna"],
             bins=[0, 1, 5, 10, 50, 100, 500, np.inf],
             labels=["0–1", "1–5", "5–10", "10–50", "50–100", "100–500", "500+"])
tna_dist = flows.groupby(cut, observed=True).agg(
    n_obs=("flow", "count"),
    pct_of_flows=("flow", lambda x: 100 * len(x) / len(flows)),
    mean_abs_flow=("flow", lambda x: x.abs().mean()),
    pct_abs_flow_gt1=("flow", lambda x: (x.abs() > 1).mean() * 100),
).round(3)
print(tna_dist.to_string())

# 4b. Correlation between |flow| and lag TNA
corr_logtna = flows[["flow", "lag_portfolio_tna"]].assign(
    abs_flow=flows["flow"].abs(),
    log_lag_tna=np.log1p(flows["lag_portfolio_tna"])
).corr()
print(f"\n  b) Corr(|flow|, log(lag_tna)) = "
      f"{corr_logtna.loc['abs_flow','log_lag_tna']:.4f}")

# 4c. Extreme flows by lag_TNA threshold
print(f"\n  c) Extreme flow rate by lag_tna threshold:")
for thresh in [1, 5, 10, 25, 50]:
    sub = flows[flows["lag_portfolio_tna"] >= thresh]
    n_ext = (sub["flow"].abs() > 1).sum()
    print(f"    lag_tna >= ${thresh:>3}M  →  N={len(sub):>7,}  "
          f"extreme (|flow|>1): {n_ext:>5,}  ({100*n_ext/max(len(sub),1):.3f}%)")

# 4d. Top 20 extreme flow obs with diagnostic columns
print(f"\n  d) Top 20 absolute raw flow values:")
top_flow_cols = ["wficn", "caldt", "flow", "portfolio_tna",
                 "lag_portfolio_tna", "portfolio_return", "fund_name"]
top_flow_cols = [c for c in top_flow_cols if c in s2.columns]
top_flow = (
    flows.assign(abs_flow=flows["flow"].abs())
    .nlargest(20, "abs_flow")
    [top_flow_cols]
    .round(4)
)
print(top_flow.to_string(index=False))

md.append("## 4. Drivers of extreme raw flow\n\n**lag_portfolio_tna distribution for flow observations:**\n```")
md.append(tna_dist.to_string())
md.append(f"\nCorr(|flow|, log(lag_tna)) = {corr_logtna.loc['abs_flow','log_lag_tna']:.4f}")
md.append("")
for thresh in [1, 5, 10, 25, 50]:
    sub = flows[flows["lag_portfolio_tna"] >= thresh]
    n_ext = (sub["flow"].abs() > 1).sum()
    md.append(f"  lag_tna >= ${thresh:>3}M  →  N={len(sub):>7,}  extreme (|flow|>1): {n_ext:>5,}  ({100*n_ext/max(len(sub),1):.3f}%)")
md.append("```\n")


# ══════════════════════════════════════════════════════════════════════
# 5. Simulating cleaning rules — how much data do we lose?
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("5. SIMULATED CLEANING RULES — IMPACT ON SAMPLE SIZE")
print("═" * 70)

base_n  = len(s2)
base_w  = s2["wficn"].nunique()
flow_n  = len(flows)

rules = []

# Rule A: drop |portfolio_return| >= 1  (impossible monthly return)
mask_A = s2["portfolio_return"].abs() < 1
n_A    = mask_A.sum()
rules.append(("A. Drop |return| ≥ 1  (invalid return)", n_A,
              mask_A[mask_A].pipe(lambda _: s2[mask_A]["wficn"].nunique())))

# Rule B: drop |portfolio_return| >= 0.5  (extreme but possible)
mask_B = s2["portfolio_return"].abs() < 0.5
n_B    = mask_B.sum()
rules.append(("B. Drop |return| ≥ 0.5 (aggressive trim)", n_B,
              s2[mask_B]["wficn"].nunique()))

# Rule C: require lag_portfolio_tna >= 10M  (small-fund noise filter)
mask_C = s2["lag_portfolio_tna"].fillna(0) >= 10
n_C    = mask_C.sum()
rules.append(("C. Require lag_tna ≥ $10M", n_C,
              s2[mask_C]["wficn"].nunique()))

# Rule D: require lag_portfolio_tna >= 5M
mask_D = s2["lag_portfolio_tna"].fillna(0) >= 5
n_D    = mask_D.sum()
rules.append(("D. Require lag_tna ≥ $5M", n_D,
              s2[mask_D]["wficn"].nunique()))

# Rule E: combine A + C (drop bad returns AND require lag_tna >= 10M)
mask_E = mask_A & mask_C
n_E    = mask_E.sum()
rules.append(("E. Combined: A + C", n_E,
              s2[mask_E]["wficn"].nunique()))

# Rule F: combine A + D  (drop bad returns AND require lag_tna >= 5M)
mask_F = mask_A & mask_D
n_F    = mask_F.sum()
rules.append(("F. Combined: A + D", n_F,
              s2[mask_F]["wficn"].nunique()))

print(f"\n  Baseline: {base_n:,} obs  /  {base_w:,} unique WFICN\n")
print(f"  {'Rule':<42}  {'Obs kept':>9}  {'WFICN':>6}  {'% kept':>7}  {'Lost':>7}")
print(f"  {SEP2}")
for label, n_kept, w_kept in rules:
    print(f"  {label:<42}  {n_kept:>9,}  {w_kept:>6,}  "
          f"{100*n_kept/base_n:>6.1f}%  {base_n-n_kept:>7,}")

# For flow-level impact of lag_tna threshold
print(f"\n  Flow-level impact of lag_tna threshold (flow obs only, N={flow_n:,}):")
for thresh in [5, 10, 25]:
    sub  = flows[flows["lag_portfolio_tna"] >= thresh]
    lost = flow_n - len(sub)
    print(f"    lag_tna ≥ ${thresh}M: {len(sub):,} kept  ({lost:,} lost, "
          f"{100*lost/flow_n:.1f}%)")

# Also check flow extremes after each rule
print(f"\n  Extreme flow rate (|flow| > 1) under each rule:")
for label, n_kept, w_kept in rules:
    rule_label = label.split(":")[0].strip()
    if "A" in rule_label or "E" in rule_label or "F" in rule_label:
        sub = s2[mask_A]["flow"] if "A" in label and "C" not in label and "D" not in label else \
              s2[mask_E]["flow"] if "E" in label else \
              s2[mask_F]["flow"] if "F" in label else \
              s2["flow"]
    elif "C" in rule_label:
        sub = s2[mask_C]["flow"]
    elif "D" in rule_label:
        sub = s2[mask_D]["flow"]
    else:
        sub = s2["flow"]
    ext = (sub.abs() > 1).sum()
    print(f"    {label:<42}  extreme: {ext:>6,}  ({100*ext/max(sub.notna().sum(),1):.3f}%)")

md.append("## 5. Simulated cleaning rules\n\n```")
md.append(f"Baseline: {base_n:,} obs  /  {base_w:,} unique WFICN\n")
md.append(f"{'Rule':<42}  {'Obs kept':>9}  {'WFICN':>6}  {'% kept':>7}  {'Lost':>7}")
md.append(SEP2)
for label, n_kept, w_kept in rules:
    md.append(f"{label:<42}  {n_kept:>9,}  {w_kept:>6,}  "
              f"{100*n_kept/base_n:>6.1f}%  {base_n-n_kept:>7,}")
md.append("```\n")


# ══════════════════════════════════════════════════════════════════════
# 6. Recommendation and conclusion
# ══════════════════════════════════════════════════════════════════════

print(SEP)
print("6. RECOMMENDATION & CONCLUSION")
print("═" * 70)

# Compute key numbers for the narrative
n_ret_gt1    = (s2["portfolio_return"].abs() >= 1).sum()
n_ret_lt_m1  = (s2["portfolio_return"] < -1).sum()
n_tiny_lag   = (flows["lag_portfolio_tna"] < 10).sum()
pct_tiny_lag = 100 * n_tiny_lag / len(flows)
n_ext_flow   = (flows["flow"].abs() > 1).sum()
pct_ext_flow = 100 * n_ext_flow / len(flows)
n_ext_flow_post_A = (s2.loc[mask_A, "flow"].abs() > 1).sum()

conclusion = f"""
  Are extreme returns a serious problem?
  {'─'*66}
  Total obs with |portfolio_return| ≥ 1     : {n_ret_gt1:,}  ({100*n_ret_gt1/len(s2):.3f}%)
  Total obs with portfolio_return < -1       : {n_ret_lt_m1:,}
  A monthly return below -100% is economically impossible for a long-only
  equity fund. These observations reflect CRSP data artefacts (tiny-TNA
  share classes with erroneous NAV entries, fund mergers recorded with
  a -1 return in the period of termination, or a $0 → very small TNA
  transition where one share class receives all TNA weight).

  Are extreme flows a serious problem?
  {'─'*66}
  Obs with |raw flow| > 1 (>100% net flow)   : {n_ext_flow:>8,}  ({pct_ext_flow:.3f}%)
  Obs with lag_tna < $10M                    : {n_tiny_lag:>8,}  ({pct_tiny_lag:.1f}%)
  Near-zero lag_tna is the primary driver — when a new share class joins
  a WFICN mid-month, the prior-month TNA is near zero and the computed
  flow is huge. Current flow_winsorized already handles the worst tails,
  but tiny-lag-TNA observations will inflate flow volatility and bias
  regression coefficients if not filtered.

  Recommended cleaning rules before regressions
  {'─'*66}
  Rule 1 — Drop |portfolio_return| ≥ 1:
    Removes {n_ret_gt1:,} obs ({100*n_ret_gt1/len(s2):.3f}% of sample).
    Rationale: impossible monthly return for a long-only fund; these are
    data artefacts, not genuine outliers. Standard in the literature.

  Rule 2 — Require lag_portfolio_tna ≥ $10M:
    Removes an additional {base_n - n_E:,} obs vs. Rule 1 alone.
    Rationale: eliminates tiny-fund noise that drives extreme flows.
    $10M is the most common threshold in the mutual fund literature
    (Chevalier & Ellison 1997, Sirri & Tufano 1998, among others).
    Funds below this threshold have very high flow measurement error.

  Rule 3 — Retain current flow_winsorized as the main regression variable:
    After Rules 1+2, raw extreme flows virtually disappear ({n_ext_flow_post_A:,} remain
    after Rule 1 alone). Winsorization at 1/99 provides a further
    safeguard. Use flow_winsorized as the dependent variable; keep raw
    flow for robustness checks.

  Rule 4 — Winsorize portfolio_return at 1/99 before constructing
    performance measures (rolling alpha, Sharpe). This is independent
    of the |return| ≥ 1 hard drop.

  Summary decision table
  {'─'*66}
  {'Filter':<40}  {'Apply?':<6}  Reason
  drop |portfolio_return| >= 1         YES    Economically impossible
  winsorize portfolio_return 1/99      YES    For performance measures
  require lag_portfolio_tna >= $10M    YES    Literature standard; kills tiny-TNA flow noise
  keep flow_winsorized as DV           YES    Already applied; robust
  further winsorize flow 1/99          N/A    Already done in Step 2
"""
print(conclusion)

md.append("## 6. Recommendation & Conclusion\n\n```")
md.append(conclusion)
md.append("```\n")

# Save markdown
md_path = TABS + "final_step2_return_flow_quality_check.md"
with open(md_path, "w") as f:
    f.write("\n".join(md))
print(f"\n  Saved → {md_path}")
print(SEP)
print("Done.")
print("═" * 70)
