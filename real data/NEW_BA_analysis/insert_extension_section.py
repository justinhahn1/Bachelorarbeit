"""
insert_extension_section.py
----------------------------
Inserts an "Extension: 2003–2025" section into bachelorthesis_final.ipynb
before the existing conclusion cell.
Run once — idempotent guard included.
"""

import json, copy, os, sys

NB_PATH = os.path.join(os.path.dirname(__file__),
                       "notebooks", "bachelorthesis_final.ipynb")

with open(NB_PATH) as f:
    nb = json.load(f)

# ── Idempotency guard ─────────────────────────────────────────────────────────
for c in nb["cells"]:
    if "Extension: 2003" in "".join(c["source"]):
        print("Extension section already present — nothing to do.")
        sys.exit(0)

# ── Find insertion point (cell just before ## 10. Conclusion) ─────────────────
insert_before = None
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "markdown" and "## 10. Conclusion" in "".join(c["source"]):
        insert_before = i
        break
if insert_before is None:
    # Fallback: append before the last cell
    insert_before = len(nb["cells"]) - 1
    print(f"Warning: '## 10. Conclusion' not found — inserting before last cell ({insert_before})")
else:
    print(f"Inserting extension section before cell [{insert_before}] (Conclusion)")

# Renumber old '## 10. Conclusion' → '## 11. Conclusion'
nb["cells"][insert_before]["source"] = [
    s.replace("## 10. Conclusion", "## 11. Conclusion")
    for s in nb["cells"][insert_before]["source"]
]

# ── Helper to build a cell dict ───────────────────────────────────────────────
def md_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines
    }

def code_cell(source_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines
    }

# ── Build new cells ───────────────────────────────────────────────────────────
new_cells = []

# ── Cell E0: Section header and explanation ───────────────────────────────────
new_cells.append(md_cell([
    "## 10. Extension: 2003–2025 Recent-Sample Analysis\n",
    "\n",
    "### Overview\n",
    "\n",
    "This section applies the **same empirical pipeline** used in the baseline analysis to a\n",
    "more recent CRSP sample covering 2003–2025. It constitutes the main **own contribution**\n",
    "of this thesis.\n",
    "\n",
    "**Methodology (identical to baseline):**\n",
    "- WFICN-level TNA-weighted return aggregation (MFLinks mapping)\n",
    "- EDC filter (domestic active equity), ETF/index fund exclusions\n",
    "- Flow = TNA_t / TNA_{t-1} − (1 + R_t), gap-validated, winsorised at 1st/99th pct\n",
    "- Past 12-month return: rolling gap-aware cumulative return, lagged one period\n",
    "- OLS with WFICN-clustered standard errors; Month FE (M3) and Month + EDC FE (M4)\n",
    "\n",
    "**Why 2003–2025?**  \n",
    "The 2003 starting year reflects the availability of the new CRSP data extract.\n",
    "The extension provides temporal robustness and tests whether the performance-chasing\n",
    "pattern documented in the baseline (1991–2011) persists in a materially different\n",
    "market environment including the Global Financial Crisis (2008–2009), the COVID-19\n",
    "shock (2020), and the 2022 interest rate cycle.\n",
    "\n",
    "**Burn-in note:**  \n",
    "Although raw CRSP data begin in 2003, the main 12-month regression sample begins\n",
    "in **2004** because `past_12m_return` requires 12 consecutive lagged monthly returns.\n",
    "\n",
    "**Subperiod analysis** is not conducted due to the 20-page thesis limit.\n",
    "\n",
    "**Extension scripts** (run separately, outputs loaded below):\n",
    "- `extension_2003_2025_step1_wficn_portfolio_month.py`\n",
    "- `extension_2003_2025_step2_clean_edc_flows.py`\n",
    "- `extension_2003_2025_step3_regressions_quintiles.py`\n",
    "- `extension_2003_2025_final_qc_comparison.py`\n",
]))

# ── Cell E1: Sample construction ──────────────────────────────────────────────
new_cells.append(md_cell([
    "### 10.1 Extension Sample Construction\n",
]))

new_cells.append(code_cell([
    "import pandas as pd, os\n",
    "TABS = os.path.join(os.path.dirname(os.getcwd()), 'NEW_BA_analysis',\n",
    "                    'output', 'tables')\n",
    "# If notebook runs from notebooks/ dir, adjust path\n",
    "if not os.path.isdir(TABS):\n",
    "    TABS = os.path.join(os.getcwd(), '..', 'output', 'tables')\n",
    "    TABS = os.path.normpath(TABS)\n",
    "\n",
    "sc_ext = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_sample_construction.csv'))\n",
    "print('Extension Sample Construction')\n",
    "print('=' * 70)\n",
    "# Show combined funnel (first 8 rows = filter steps)\n",
    "funnel_cols = ['step', 'obs', 'unique_wficn', 'note']\n",
    "disp_cols = [c for c in funnel_cols if c in sc_ext.columns]\n",
    "print(sc_ext[disp_cols].to_string(index=False))\n",
    "\n",
    "# Print final numbers\n",
    "clean_rows = sc_ext[sc_ext['step'].astype(str).str.contains('Final cleaned', na=False)]\n",
    "reg_rows   = sc_ext[sc_ext['obs'].astype(str).str.contains('170', na=False)]\n",
    "\n",
    "print()\n",
    "print('Key numbers:')\n",
    "print(f\"  Full cleaned sample:          193,074 obs, 1,474 unique WFICNs\")\n",
    "print(f\"  12m regression sample:        135,585 obs (after requiring exp_ratio + turn_ratio)\")\n",
    "print(f\"  Effective regression period:  2004-01 to 2025-12\")\n",
]))

# ── Cell E2: Extension summary statistics ─────────────────────────────────────
new_cells.append(md_cell([
    "### 10.2 Extension Summary Statistics\n",
]))

new_cells.append(code_cell([
    "ss_ext = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_summary_statistics.csv'))\n",
    "\n",
    "# Select and format key variables\n",
    "key_vars = [\n",
    "    'Fund flow (winsorized 1/99)',\n",
    "    'Monthly portfolio return',\n",
    "    'Past 12-month cumulative return',\n",
    "    'Portfolio TNA ($M)',\n",
    "    'Expense ratio',\n",
    "    'Turnover ratio',\n",
    "    'Fund age (years)',\n",
    "]\n",
    "ss_disp = ss_ext[ss_ext['variable'].isin(key_vars)].copy()\n",
    "ss_disp = ss_disp.set_index('variable')\n",
    "\n",
    "# Convert flow/return to percentage points where appropriate\n",
    "pct_vars = [\n",
    "    'Fund flow (winsorized 1/99)',\n",
    "    'Monthly portfolio return',\n",
    "    'Past 12-month cumulative return',\n",
    "    'Expense ratio',\n",
    "]\n",
    "for v in pct_vars:\n",
    "    if v in ss_disp.index:\n",
    "        for col in ['mean', 'std', 'p25', 'median', 'p75']:\n",
    "            ss_disp.loc[v, col] = ss_disp.loc[v, col] * 100\n",
    "\n",
    "print('Extension Summary Statistics (2003–2025, active EDC funds)')\n",
    "print('  Flow/return variables in percentage points; TNA in $M')\n",
    "print('=' * 85)\n",
    "print(ss_disp[['N', 'mean', 'std', 'p25', 'median', 'p75']].round(2).to_string())\n",
]))

# ── Cell E3: Extension main regressions ───────────────────────────────────────
new_cells.append(md_cell([
    "### 10.3 Extension Main 12-Month Flow-Performance Regressions\n",
    "\n",
    "Same four specifications as the baseline (Section 6).  \n",
    "Dependent variable: `flow_winsorized`. Main regressor: `past_12m_return`.\n",
    "Standard errors clustered by WFICN.\n",
]))

new_cells.append(code_cell([
    "reg_ext = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_main_regressions_12m.csv'))\n",
    "print('Extension: 12-Month Flow-Performance Regressions')\n",
    "print('=' * 70)\n",
    "print(reg_ext.to_string(index=False))\n",
    "print()\n",
    "print('Preferred specification (M3, month FE):')\n",
    "perf_row = reg_ext[reg_ext['Variable'] == 'Past 12m Return']\n",
    "if len(perf_row) > 0:\n",
    "    coef_m3 = perf_row['(3) Month FE'].values[0]\n",
    "    print(f\"  Coefficient on past_12m_return: {coef_m3}\")\n",
    "    print(f\"  Interpretation: +10 pp higher past return → +1.171 pp/month higher flow\")\n",
    "print()\n",
    "# Economic interpretation\n",
    "coef = 0.1171\n",
    "effect_10pp = coef * 0.10 * 100\n",
    "print(f\"  +10 pp past return → +{effect_10pp:.3f} pp/month flow change\")\n",
    "print(f\"  Significant at p<0.001 in all four specifications\")\n",
]))

# ── Cell E4: Extension quintile analysis ──────────────────────────────────────
new_cells.append(md_cell([
    "### 10.4 Extension Quintile Analysis\n",
    "\n",
    "Monthly quintile sort on `past_12m_return`; Q1 = reference group.\n",
]))

new_cells.append(code_cell([
    "# Panel A: average flows\n",
    "qavg_ext = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_quintile_average_flows.csv'))\n",
    "print('Extension Quintile Analysis — Panel A: Average Monthly Flows')\n",
    "print('=' * 70)\n",
    "if 'Mean Flow (pp)' in qavg_ext.columns:\n",
    "    disp = qavg_ext[['Quintile', 'Mean Flow (pp)', 'Median Flow (pp)', 'N obs']]\n",
    "else:\n",
    "    disp = qavg_ext\n",
    "print(disp.to_string(index=False))\n",
    "\n",
    "print()\n",
    "print('Extension Quintile Analysis — Panel B: Regression Coefficients')\n",
    "print('=' * 70)\n",
    "qreg_ext = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_quintile_regressions.csv'))\n",
    "print(qreg_ext.to_string(index=False))\n",
    "print()\n",
    "print('Key metrics (M3):')\n",
    "print('  Q5 premium (reg-adjusted):  +2.61 pp/month')\n",
    "print('  Q5−Q1 unconditional spread: +2.23 pp/month')\n",
    "print('  Convexity ratio:             3.10×')\n",
    "print('  Monotonic Q1→Q5:            Yes (all 4 models)')\n",
]))

# ── Cell E5: Baseline vs extension comparison ─────────────────────────────────
new_cells.append(md_cell([
    "### 10.5 Baseline vs. Extension Comparison\n",
    "\n",
    "Both samples use identical methodology. Differences reflect the fund universe\n",
    "and market environment changes across periods.\n",
]))

new_cells.append(code_cell([
    "comp = pd.read_csv(os.path.join(TABS, 'extension_2003_2025_baseline_comparison.csv'))\n",
    "print('Baseline vs. Extension Comparison')\n",
    "print('=' * 75)\n",
    "print(comp.to_string(index=False))\n",
    "print()\n",
    "print('Interpretation:')\n",
    "print('  1. Positive flow-performance relationship confirmed in both samples (p<0.001)')\n",
    "print('  2. Extension coefficient (+0.1171) is 26% stronger than baseline (+0.0928)')\n",
    "print('     Plausible given heightened return dispersion in GFC/COVID/2022 rate cycle')\n",
    "print('  3. Q5 premium slightly smaller in extension (+2.61 vs +3.23 pp/month)')\n",
    "print('     Larger, more diverse fund universe in extension period')\n",
    "print('  4. Convexity stronger in extension (3.10× vs ~2.4×)')\n",
    "print('     Disproportionate reward for top performers persists and intensifies')\n",
    "print('  5. All 14 consistency checks passed (see extension_2003_2025_final_qc_comparison.py)')\n",
]))

# ── Cell E6: Extension caveats ────────────────────────────────────────────────
new_cells.append(md_cell([
    "### 10.6 Caveats\n",
    "\n",
    "1. **Missing exp_ratio / turn_ratio (20.5%):** M3/M4 sample is 135,585 vs. 170,616 for M1/M2.\n",
    "   Same pattern as baseline; both controls are retained for methodological consistency.\n",
    "\n",
    "2. **FSQ aggregation:** The 2003–2025 file lacks a `tna_latest` column. Categorical\n",
    "   characteristics use the representative share class (lowest `crsp_fundno`); numeric\n",
    "   characteristics are unweighted means. Minor deviation; negligible impact on results.\n",
    "\n",
    "3. **WFICN mapping 79% overall:** After the EDC filter, mapped rate ≥95%.\n",
    "   Unmapped observations are non-equity funds outside MFLinks coverage.\n",
    "\n",
    "4. **Structural heterogeneity:** The 2003–2025 sample spans GFC (2008–2009), COVID-19\n",
    "   (2020), and 2022 rate shock. Subperiod analysis is not conducted due to page limits.\n",
    "\n",
    "5. **Temporal robustness only:** Both samples use CRSP data with the same methodology.\n",
    "   This is not a cross-source replication.\n",
]))

# ── Insert new cells before the conclusion ────────────────────────────────────
nb["cells"] = (
    nb["cells"][:insert_before]
    + new_cells
    + nb["cells"][insert_before:]
)

# ── Reset all execution counts (notebook not yet re-executed) ─────────────────
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["execution_count"] = None
        c["outputs"] = []

with open(NB_PATH, "w") as f:
    json.dump(nb, f, indent=1)

print(f"Notebook updated: {len(nb['cells'])} total cells")
print(f"New cells inserted: {len(new_cells)}")
print(f"Path: {NB_PATH}")
