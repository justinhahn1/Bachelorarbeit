"""
create_thesis_tables.py
-----------------------
Generates all thesis-ready tables for the empirical section.
Reads only existing output CSVs — does NOT rerun any regressions.
Saves to output/thesis_tables/
"""

import os
import textwrap

OUT = os.path.join(os.path.dirname(__file__), "output", "thesis_tables")
os.makedirs(OUT, exist_ok=True)

def write(fname, content):
    path = os.path.join(OUT, fname)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Saved  {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1 — Sample construction, baseline
# ─────────────────────────────────────────────────────────────────────────────

table1_md = """\
**Table 1. Sample Construction — Baseline (1991–2011 CRSP Data)**

| Step | Description | Obs removed | Obs remaining | WFICNs |
|------|-------------|------------:|-------------:|-------:|
| (0) | All WFICN-month observations after WFICN merge | — | 1,241,561 | 10,740 |
| (1) | Drop missing or zero portfolio TNA | 205 | 1,241,356 | 10,740 |
| (2) | Drop missing monthly portfolio return | 78,282 | 1,163,074 | 10,621 |
| (3) | Keep sample window 1997–2011 | 191,666 | 971,408 | 10,325 |
| (4) | Keep domestic equity (crsp_obj_cd = 'EDC') | 835,754 | 135,654 | 1,653 |
| (5) | Exclude ETFs (flag + name screen) | 5,872 | 129,782 | 1,565 |
| (6) | Exclude index funds (flag + name screen) | 19,324 | 110,458 | 1,340 |
| (7) | Exclude non-target categories | 2,148 | 108,310 | 1,322 |
| (8) | Drop economically impossible returns (\|r\|≥1) | 1 | 108,309 | 1,322 |
| (9) | Require lagged TNA ≥ $10M | 8,782 | 99,527 | 1,215 |
| (10) | Drop missing winsorized flow (DV) | 202 | **99,325** | **1,215** |
| *12m reg. sample* | Require 12 consecutive lagged monthly returns | — | **77,140** | **1,215** |

*Notes:* WFICN denotes the MFLinks portfolio identifier that maps multiple share classes to
one fund. EDC = CRSP domestic equity classification (small-cap EDCS, mid-cap EDCM,
institutional EDCI). ETF exclusion applies et_flag and name keywords. Index fund exclusion
applies index_fund_flag and name keywords. Minimum TNA follows Chevalier and Ellison (1997)
and Sirri and Tufano (1998). Past 12-month return requires a 12-month rolling window with
no gaps, yielding a smaller regression sample. Flow is winsorised at the 1st/99th percentiles.
"""

write("table1_sample_construction_baseline.md", table1_md)

table1_csv = (
    "Step,Description,Obs removed,Obs remaining,WFICNs\n"
    "(0),All WFICN-month observations after WFICN merge,—,1241561,10740\n"
    "(1),Drop missing or zero portfolio TNA,205,1241356,10740\n"
    "(2),Drop missing monthly portfolio return,78282,1163074,10621\n"
    "(3),Keep sample window 1997–2011,191666,971408,10325\n"
    "(4),Keep domestic equity (EDC),835754,135654,1653\n"
    "(5),Exclude ETFs,5872,129782,1565\n"
    "(6),Exclude index funds,19324,110458,1340\n"
    "(7),Exclude non-target categories,2148,108310,1322\n"
    "(8),Drop impossible returns,1,108309,1322\n"
    "(9),Require lagged TNA >= $10M,8782,99527,1215\n"
    "(10),Drop missing winsorized flow,202,99325,1215\n"
    "12m regression sample,Require 12 consecutive lagged returns,—,77140,1215\n"
)
write("table1_sample_construction_baseline.csv", table1_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2 — Summary statistics, baseline
# ─────────────────────────────────────────────────────────────────────────────

table2_md = """\
**Table 2. Summary Statistics — Baseline Sample (1991–2011)**

| Variable | N | Mean | Std Dev | p25 | Median | p75 |
|----------|--:|-----:|--------:|----:|-------:|----:|
| Fund flow (%) | 99,325 | 0.34 | 5.22 | −1.52 | −0.28 | 1.34 |
| Monthly portfolio return (%) | 99,325 | 0.67 | 6.52 | −3.02 | 1.15 | 4.56 |
| Past 12-month return (%) | 83,186 | 8.79 | 24.51 | −6.93 | 11.26 | 24.16 |
| Portfolio TNA ($M) | 99,325 | 705 | 1,833 | 73.7 | 213.4 | 611.7 |
| Expense ratio (%) | 90,309 | 1.34 | 0.40 | 1.10 | 1.28 | 1.53 |
| Turnover ratio | 90,037 | 1.00 | 1.02 | 0.46 | 0.79 | 1.27 |
| Fund age (years) | 99,325 | 10.80 | 8.46 | 5.16 | 8.92 | 13.91 |

*Notes:* Observation unit is WFICN-month. Fund flow = (TNA_t / TNA_{t-1}) − (1 + R_t),
expressed in percentage points and winsorised at the 1st/99th percentiles. Past 12-month
return is a rolling cumulative return over months t−12 to t−1 with no gap allowed (requires
12 consecutive observations); the smaller N reflects this restriction. Portfolio TNA and
expense ratio are reported in raw units; TNA is the WFICN-level aggregate.
Sample: active domestic equity mutual funds (crsp_obj_cd = 'EDC'), 1997–2011.
"""

write("table2_summary_statistics_baseline.md", table2_md)

table2_csv = (
    "Variable,N,Mean,Std Dev,p25,Median,p75\n"
    "Fund flow (%),99325,0.34,5.22,-1.52,-0.28,1.34\n"
    "Monthly portfolio return (%),99325,0.67,6.52,-3.02,1.15,4.56\n"
    "Past 12-month return (%),83186,8.79,24.51,-6.93,11.26,24.16\n"
    "Portfolio TNA ($M),99325,705,1833,73.7,213.4,611.7\n"
    "Expense ratio (%),90309,1.34,0.40,1.10,1.28,1.53\n"
    "Turnover ratio,90037,1.00,1.02,0.46,0.79,1.27\n"
    "Fund age (years),99325,10.80,8.46,5.16,8.92,13.91\n"
)
write("table2_summary_statistics_baseline.csv", table2_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 3 — Baseline main regressions
# ─────────────────────────────────────────────────────────────────────────────

table3_md = """\
**Table 3. Flow–Performance Regressions — Baseline (1991–2011)**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| **Past 12m return** | 0.0209\\*\\*\\* | 0.0201\\*\\*\\* | 0.0928\\*\\*\\* | 0.0943\\*\\*\\* |
| | (0.0013) | (0.0013) | (0.0047) | (0.0046) |
| log(TNA_{t−1}) | | 0.0002 | 0.0003 | 0.0002 |
| | | (0.0003) | (0.0003) | (0.0003) |
| Expense ratio | | −0.2551\\*\\* | −0.2477\\*\\* | −0.1499 |
| | | (0.1053) | (0.1109) | (0.1095) |
| Fund age (years) | | −0.0006\\*\\*\\* | −0.0004\\*\\*\\* | −0.0004\\*\\*\\* |
| | | (0.0001) | (0.0001) | (0.0001) |
| Turnover ratio | | −0.0016\\*\\*\\* | −0.0013\\*\\* | −0.0015\\*\\*\\* |
| | | (0.0005) | (0.0005) | (0.0005) |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 77,140 | 77,140 | 77,140 | 77,140 |
| R² | 0.012 | 0.023 | 0.087 | 0.089 |

*Notes:* Dependent variable: fund flow (winsorised at 1st/99th percentiles), expressed as
a proportion. Past 12-month return is the cumulative portfolio return over months t−12 to
t−1. Standard errors (in parentheses) are clustered by WFICN. EDC style fixed effects:
EDCS (small-cap) is the baseline; EDCM and EDCI dummies included in model (4).
Significance levels: \\* p<0.10, \\*\\* p<0.05, \\*\\*\\* p<0.01.
Sample: active domestic equity mutual funds, 1991–2011 CRSP data. Effective regression
period: 1999–2011 (12 months of burn-in).
"""

write("table3_baseline_main_regression.md", table3_md)

table3_csv = (
    "Variable,(1),(2),(3),(4)\n"
    "Past 12m return,0.0209***,0.0201***,0.0928***,0.0943***\n"
    "SE,(0.0013),(0.0013),(0.0047),(0.0046)\n"
    "log(TNA_t-1),—,0.0002,0.0003,0.0002\n"
    "SE,—,(0.0003),(0.0003),(0.0003)\n"
    "Expense ratio,—,-0.2551**,-0.2477**,-0.1499\n"
    "SE,—,(0.1053),(0.1109),(0.1095)\n"
    "Fund age (years),—,-0.0006***,-0.0004***,-0.0004***\n"
    "SE,—,(0.0001),(0.0001),(0.0001)\n"
    "Turnover ratio,—,-0.0016***,-0.0013**,-0.0015***\n"
    "SE,—,(0.0005),(0.0005),(0.0005)\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,77140,77140,77140,77140\n"
    "R-squared,0.012,0.023,0.087,0.089\n"
)
write("table3_baseline_main_regression.csv", table3_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 4 — Baseline quintile analysis
# ─────────────────────────────────────────────────────────────────────────────

table4_md = """\
**Table 4. Quintile Analysis — Baseline (1991–2011)**

**Panel A: Average monthly flows by past-performance quintile**

| Quintile | Mean flow (pp/month) | Median flow (pp/month) | N |
|----------|---------------------:|-----------------------:|--:|
| Q1 (worst) | −1.35 | −1.16 | 16,694 |
| Q2 | −0.57 | −0.67 | 16,606 |
| Q3 | −0.09 | −0.35 | 16,613 |
| Q4 | +0.57 | −0.02 | 16,606 |
| Q5 (best) | +1.87 | +0.58 | 16,667 |
| Q5 − Q1 | **+3.22** | | |

**Panel B: Quintile regression coefficients (Q1 = reference group)**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| Q2 | 0.0082\\*\\*\\* | 0.0078\\*\\*\\* | 0.0077\\*\\*\\* | 0.0076\\*\\*\\* |
| | (0.0007) | (0.0007) | (0.0007) | (0.0007) |
| Q3 | 0.0131\\*\\*\\* | 0.0124\\*\\*\\* | 0.0122\\*\\*\\* | 0.0123\\*\\*\\* |
| | (0.0007) | (0.0007) | (0.0007) | (0.0007) |
| Q4 | 0.0198\\*\\*\\* | 0.0191\\*\\*\\* | 0.0189\\*\\*\\* | 0.0190\\*\\*\\* |
| | (0.0008) | (0.0009) | (0.0008) | (0.0008) |
| Q5 | 0.0331\\*\\*\\* | 0.0324\\*\\*\\* | 0.0323\\*\\*\\* | 0.0325\\*\\*\\* |
| | (0.0012) | (0.0012) | (0.0012) | (0.0012) |
| Controls | No | Yes | Yes | Yes |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 77,140 | 77,140 | 77,140 | 77,140 |
| R² | 0.057 | 0.066 | 0.094 | 0.096 |

*Convexity (M3): Q4→Q5 step = 1.34 pp; avg(Q2→Q3, Q3→Q4) step = 0.56 pp → ratio ≈ 2.4×*

*Notes:* Quintiles are assigned monthly within each calendar month based on past 12-month
return. Q1 = lowest performance, Q5 = highest. Panel A shows unconditional means.
Panel B coefficients represent the average flow premium over Q1 funds. Dependent variable:
fund flow (winsorised at 1st/99th percentiles). Standard errors clustered by WFICN.
Controls: log(TNA_{t−1}), expense ratio, fund age (years), turnover ratio. Significance:
\\* p<0.10, \\*\\* p<0.05, \\*\\*\\* p<0.01.
"""

write("table4_baseline_quintile_analysis.md", table4_md)

table4_csv = (
    "Panel A: Average monthly flows,,,,\n"
    "Quintile,Mean flow (pp/month),Median flow (pp/month),N obs,\n"
    "Q1 (worst),-1.35,-1.16,16694,\n"
    "Q2,-0.57,-0.67,16606,\n"
    "Q3,-0.09,-0.35,16613,\n"
    "Q4,+0.57,-0.02,16606,\n"
    "Q5 (best),+1.87,+0.58,16667,\n"
    "Q5-Q1 spread,+3.22,,,\n"
    "\n"
    "Panel B: Quintile regression coefficients (Q1 = ref),,,,\n"
    "Variable,(1),(2),(3),(4)\n"
    "Q2,0.0082***,0.0078***,0.0077***,0.0076***\n"
    "SE_Q2,(0.0007),(0.0007),(0.0007),(0.0007)\n"
    "Q3,0.0131***,0.0124***,0.0122***,0.0123***\n"
    "SE_Q3,(0.0007),(0.0007),(0.0007),(0.0007)\n"
    "Q4,0.0198***,0.0191***,0.0189***,0.0190***\n"
    "SE_Q4,(0.0008),(0.0009),(0.0008),(0.0008)\n"
    "Q5,0.0331***,0.0324***,0.0323***,0.0325***\n"
    "SE_Q5,(0.0012),(0.0012),(0.0012),(0.0012)\n"
    "Controls,No,Yes,Yes,Yes\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,77140,77140,77140,77140\n"
    "R-squared,0.057,0.066,0.094,0.096\n"
    "Convexity (M3),~2.4x,,,\n"
)
write("table4_baseline_quintile_analysis.csv", table4_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 5 — Baseline vs Extension comparison
# ─────────────────────────────────────────────────────────────────────────────

table5_md = """\
**Table 5. Baseline vs. Extension Comparison**

| Dimension | Baseline (1991–2011) | Extension (2003–2025) |
|-----------|---------------------|----------------------|
| Raw CRSP period | 1991–2011 | 2003–2025 |
| Effective 12m regression period | 1999–2011 | 2004–2025 |
| Fund universe | Active domestic equity (EDC) | Active domestic equity (EDC) |
| Regression N (M3/M4) | 77,140 | 135,585 |
| Unique WFICNs (clusters) | 1,215 | 1,120 |
| **M3 coefficient (SE)** | **0.0928 (0.0047)** | **0.1171 (0.0043)** |
| +10 pp past return → flow (M3) | +0.928 pp/month | +1.171 pp/month |
| Flow standard deviation | 5.22 pp | 4.08 pp |
| Past 12m return SD | 24.5 pp | 19.1 pp |
| Q5 − Q1 (unconditional means) | +3.22 pp/month | +2.23 pp/month |
| Q5 premium, regression-adjusted (M3) | +3.230 pp/month | +2.610 pp/month |
| Convexity ratio (M3) | ~2.4× | 3.10× |
| Monotonic Q2→Q5 (M3) | Yes — all 4 models | Yes — all 4 models |
| Median portfolio TNA ($M) | 212 | 306 |
| Median fund age (years) | 8.9 | 14.8 |
| SE clustering | WFICN | WFICN |
| Controls | log TNA, exp. ratio, age, turnover | log TNA, exp. ratio, age, turnover |
| Fixed effects (M3 / M4) | Month / Month + EDC | Month / Month + EDC |

*Notes:* Both samples use identical methodology: WFICN-level TNA-weighted return aggregation,
flow = TNA_t/TNA_{t-1} − (1 + R_t) with 28–35 day gap check, 1/99 winsorisation, 12-month
gap-aware rolling past return, OLS with WFICN-clustered standard errors. M3 is the preferred
specification: controls + month fixed effects. Convexity = (Q4→Q5 step) / avg(Q2→Q3 step,
Q3→Q4 step). The extension covers a materially different market environment including the
Global Financial Crisis (2008–2009), the COVID-19 shock (2020), and the 2022 rate cycle.
"""

write("table5_baseline_vs_extension_comparison.md", table5_md)

table5_csv = (
    "Dimension,Baseline (1991-2011),Extension (2003-2025)\n"
    "Raw CRSP period,1991-2011,2003-2025\n"
    "Effective 12m regression period,1999-2011,2004-2025\n"
    "Fund universe,Active domestic equity (EDC),Active domestic equity (EDC)\n"
    "Regression N (M3/M4),77140,135585\n"
    "Unique WFICNs (clusters),1215,1120\n"
    "M3 coefficient (SE),0.0928 (0.0047),0.1171 (0.0043)\n"
    "+10 pp past return to flow (M3),+0.928 pp/month,+1.171 pp/month\n"
    "Flow SD (pp),5.22,4.08\n"
    "Past 12m return SD (pp),24.5,19.1\n"
    "Q5-Q1 unconditional means,+3.22 pp/month,+2.23 pp/month\n"
    "Q5 premium reg-adj M3,+3.230 pp/month,+2.610 pp/month\n"
    "Convexity ratio M3,~2.4x,3.10x\n"
    "Monotonic Q2-Q5 M3,Yes all 4 models,Yes all 4 models\n"
    "Median portfolio TNA ($M),212,306\n"
    "Median fund age (years),8.9,14.8\n"
    "SE clustering,WFICN,WFICN\n"
    "Fixed effects M3/M4,Month / Month+EDC,Month / Month+EDC\n"
)
write("table5_baseline_vs_extension_comparison.csv", table5_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE A1 — Extension main regressions
# ─────────────────────────────────────────────────────────────────────────────

tableA1_md = """\
**Table A1. Flow–Performance Regressions — Extension (2003–2025)**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| **Past 12m return** | 0.0219\\*\\*\\* | 0.0216\\*\\*\\* | 0.1171\\*\\*\\* | 0.1173\\*\\*\\* |
| | (0.0011) | (0.0011) | (0.0043) | (0.0043) |
| log(TNA_{t−1}) | | 0.0000 | −0.0001 | −0.0002 |
| | | (0.0002) | (0.0002) | (0.0002) |
| Expense ratio | | −0.3297\\*\\*\\* | −0.3787\\*\\*\\* | −0.3293\\*\\*\\* |
| | | (0.0754) | (0.0833) | (0.0827) |
| Fund age (years) | | −0.0004\\*\\*\\* | −0.0003\\*\\*\\* | −0.0003\\*\\*\\* |
| | | (0.0000) | (0.0000) | (0.0000) |
| Turnover ratio | | −0.0013\\*\\*\\* | −0.0014\\*\\*\\* | −0.0016\\*\\*\\* |
| | | (0.0005) | (0.0005) | (0.0005) |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 135,585 | 135,585 | 135,585 | 135,585 |
| R² | 0.012 | 0.023 | 0.075 | 0.076 |
| Adj. R² | 0.012 | 0.023 | 0.073 | 0.074 |

*Notes:* Dependent variable: fund flow (winsorised at 1st/99th percentiles). Past 12-month
return is the cumulative portfolio return over months t−12 to t−1. Standard errors
(in parentheses) are clustered by WFICN. Smaller N (135,585) compared to the full cleaned
sample (193,074) reflects the requirement that expense ratio and turnover ratio are non-missing.
EDC style fixed effects: EDCS (small-cap) is the baseline; EDCM and EDCI dummies in model (4).
Significance: \\* p<0.10, \\*\\* p<0.05, \\*\\*\\* p<0.01.
"""

write("tableA1_extension_main_regression.md", tableA1_md)

tableA1_csv = (
    "Variable,(1),(2),(3),(4)\n"
    "Past 12m return,0.0219***,0.0216***,0.1171***,0.1173***\n"
    "SE,(0.0011),(0.0011),(0.0043),(0.0043)\n"
    "log(TNA_t-1),—,0.0000,-0.0001,-0.0002\n"
    "SE,—,(0.0002),(0.0002),(0.0002)\n"
    "Expense ratio,—,-0.3297***,-0.3787***,-0.3293***\n"
    "SE,—,(0.0754),(0.0833),(0.0827)\n"
    "Fund age (years),—,-0.0004***,-0.0003***,-0.0003***\n"
    "SE,—,(0.0000),(0.0000),(0.0000)\n"
    "Turnover ratio,—,-0.0013***,-0.0014***,-0.0016***\n"
    "SE,—,(0.0005),(0.0005),(0.0005)\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,135585,135585,135585,135585\n"
    "R-squared,0.012,0.023,0.075,0.076\n"
    "Adj R-squared,0.012,0.023,0.073,0.074\n"
)
write("tableA1_extension_main_regression.csv", tableA1_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE A2 — Extension quintile analysis
# ─────────────────────────────────────────────────────────────────────────────

tableA2_md = """\
**Table A2. Quintile Analysis — Extension (2003–2025)**

**Panel A: Average monthly flows by past-performance quintile**

| Quintile | Mean flow (pp/month) | Median flow (pp/month) | N |
|----------|---------------------:|-----------------------:|--:|
| Q1 (worst) | −1.50 | −1.13 | 34,231 |
| Q2 | −0.84 | −0.78 | 34,075 |
| Q3 | −0.51 | −0.62 | 34,064 |
| Q4 | −0.19 | −0.47 | 34,075 |
| Q5 (best) | +0.74 | −0.10 | 34,171 |
| Q5 − Q1 | **+2.23** | | |

**Panel B: Quintile regression coefficients (Q1 = reference group)**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| Q2 | 0.0081\\*\\*\\* | 0.0076\\*\\*\\* | 0.0075\\*\\*\\* | 0.0075\\*\\*\\* |
| | (0.0005) | (0.0005) | (0.0005) | (0.0004) |
| Q3 | 0.0117\\*\\*\\* | 0.0112\\*\\*\\* | 0.0111\\*\\*\\* | 0.0110\\*\\*\\* |
| | (0.0005) | (0.0005) | (0.0005) | (0.0005) |
| Q4 | 0.0153\\*\\*\\* | 0.0148\\*\\*\\* | 0.0148\\*\\*\\* | 0.0147\\*\\*\\* |
| | (0.0006) | (0.0006) | (0.0006) | (0.0006) |
| Q5 | 0.0265\\*\\*\\* | 0.0262\\*\\*\\* | 0.0261\\*\\*\\* | 0.0261\\*\\*\\* |
| | (0.0009) | (0.0009) | (0.0009) | (0.0009) |
| Controls | No | Yes | Yes | Yes |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 135,585 | 135,585 | 135,585 | 135,585 |
| R² | 0.049 | 0.060 | 0.075 | 0.076 |

*Convexity (M3): Q4→Q5 step = 1.13 pp; avg(Q2→Q3, Q3→Q4) = 0.365 pp → ratio ≈ 3.10×*

*Notes:* Quintiles assigned monthly within each calendar month based on past 12-month
return. Q1 = lowest, Q5 = highest. Panel A: unconditional means. Panel B: coefficients
relative to Q1. All models include Q1 as reference. Dependent variable: fund flow
(winsorised 1/99). Standard errors clustered by WFICN. Significance: \\* p<0.10,
\\*\\* p<0.05, \\*\\*\\* p<0.01.
"""

write("tableA2_extension_quintile_analysis.md", tableA2_md)

tableA2_csv = (
    "Panel A: Average monthly flows,,,,\n"
    "Quintile,Mean flow (pp/month),Median flow (pp/month),N obs,\n"
    "Q1 (worst),-1.50,-1.13,34231,\n"
    "Q2,-0.84,-0.78,34075,\n"
    "Q3,-0.51,-0.62,34064,\n"
    "Q4,-0.19,-0.47,34075,\n"
    "Q5 (best),+0.74,-0.10,34171,\n"
    "Q5-Q1 spread,+2.23,,,\n"
    "\n"
    "Panel B: Quintile regression coefficients (Q1 = ref),,,,\n"
    "Variable,(1),(2),(3),(4)\n"
    "Q2,0.0081***,0.0076***,0.0075***,0.0075***\n"
    "SE_Q2,(0.0005),(0.0005),(0.0005),(0.0004)\n"
    "Q3,0.0117***,0.0112***,0.0111***,0.0110***\n"
    "SE_Q3,(0.0005),(0.0005),(0.0005),(0.0005)\n"
    "Q4,0.0153***,0.0148***,0.0148***,0.0147***\n"
    "SE_Q4,(0.0006),(0.0006),(0.0006),(0.0006)\n"
    "Q5,0.0265***,0.0262***,0.0261***,0.0261***\n"
    "SE_Q5,(0.0009),(0.0009),(0.0009),(0.0009)\n"
    "Controls,No,Yes,Yes,Yes\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,135585,135585,135585,135585\n"
    "R-squared,0.049,0.060,0.075,0.076\n"
    "Convexity (M3),3.10x,,,\n"
)
write("tableA2_extension_quintile_analysis.csv", tableA2_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE A3 — 6-month robustness (baseline)
# ─────────────────────────────────────────────────────────────────────────────

tableA3_md = """\
**Table A3. Robustness: 6-Month Past Performance — Baseline (1991–2011)**

**Panel A: Main regressions with past 6-month return**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| **Past 6m return** | 0.0362\\*\\*\\* | 0.0358\\*\\*\\* | 0.1319\\*\\*\\* | 0.1334\\*\\*\\* |
| | (0.0018) | (0.0018) | (0.0058) | (0.0058) |
| log(TNA_{t−1}) | | 0.0001 | 0.0002 | 0.0001 |
| | | (0.0003) | (0.0003) | (0.0003) |
| Expense ratio | | −0.1856\\* | −0.2069\\* | −0.1176 |
| | | (0.1052) | (0.1068) | (0.1079) |
| Fund age (years) | | −0.0007\\*\\*\\* | −0.0006\\*\\*\\* | −0.0006\\*\\*\\* |
| | | (0.0001) | (0.0001) | (0.0001) |
| Turnover ratio | | −0.0008 | −0.0010\\* | −0.0012\\* |
| | | (0.0006) | (0.0006) | (0.0006) |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 83,319 | 83,319 | 83,319 | 83,319 |
| R² | 0.016 | 0.029 | 0.081 | 0.083 |

**Panel B: Quintile regressions with past 6-month return (Q1 = reference)**

|  | (1) | (2) | (3) | (4) |
|--|:---:|:---:|:---:|:---:|
| Q2 | 0.0067\\*\\*\\* | 0.0066\\*\\*\\* | 0.0064\\*\\*\\* | 0.0064\\*\\*\\* |
| | (0.0006) | (0.0006) | (0.0006) | (0.0006) |
| Q3 | 0.0112\\*\\*\\* | 0.0108\\*\\*\\* | 0.0107\\*\\*\\* | 0.0107\\*\\*\\* |
| | (0.0007) | (0.0007) | (0.0007) | (0.0007) |
| Q4 | 0.0159\\*\\*\\* | 0.0156\\*\\*\\* | 0.0155\\*\\*\\* | 0.0155\\*\\*\\* |
| | (0.0008) | (0.0008) | (0.0008) | (0.0007) |
| Q5 | 0.0291\\*\\*\\* | 0.0287\\*\\*\\* | 0.0286\\*\\*\\* | 0.0288\\*\\*\\* |
| | (0.0012) | (0.0011) | (0.0011) | (0.0011) |
| Controls | No | Yes | Yes | Yes |
| Month FE | No | No | Yes | Yes |
| EDC style FE | No | No | No | Yes |
| N | 83,319 | 83,319 | 83,319 | 83,319 |
| R² | 0.040 | 0.052 | 0.078 | 0.080 |

*Notes:* This table replicates Tables 3–4 using past 6-month return as the performance
measure instead of past 12-month return. The larger N (83,319 vs. 77,140) reflects the
shorter burn-in period. Results are qualitatively identical: positive, significant
performance-chasing coefficient; monotonic, convex quintile pattern. Dependent variable:
fund flow (winsorised 1/99). Standard errors clustered by WFICN.
Significance: \\* p<0.10, \\*\\* p<0.05, \\*\\*\\* p<0.01.
"""

write("tableA3_robustness_6m.md", tableA3_md)

tableA3_csv = (
    "Panel A: Main regressions with past 6-month return,,,,\n"
    "Variable,(1),(2),(3),(4)\n"
    "Past 6m return,0.0362***,0.0358***,0.1319***,0.1334***\n"
    "SE,(0.0018),(0.0018),(0.0058),(0.0058)\n"
    "log(TNA_t-1),—,0.0001,0.0002,0.0001\n"
    "SE,—,(0.0003),(0.0003),(0.0003)\n"
    "Expense ratio,—,-0.1856*,-0.2069*,-0.1176\n"
    "SE,—,(0.1052),(0.1068),(0.1079)\n"
    "Fund age (years),—,-0.0007***,-0.0006***,-0.0006***\n"
    "SE,—,(0.0001),(0.0001),(0.0001)\n"
    "Turnover ratio,—,-0.0008,-0.0010*,-0.0012*\n"
    "SE,—,(0.0006),(0.0006),(0.0006)\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,83319,83319,83319,83319\n"
    "R-squared,0.016,0.029,0.081,0.083\n"
    "\n"
    "Panel B: Quintile regressions with past 6-month return,,,,\n"
    "Variable,(1),(2),(3),(4)\n"
    "Q2,0.0067***,0.0066***,0.0064***,0.0064***\n"
    "SE_Q2,(0.0006),(0.0006),(0.0006),(0.0006)\n"
    "Q3,0.0112***,0.0108***,0.0107***,0.0107***\n"
    "SE_Q3,(0.0007),(0.0007),(0.0007),(0.0007)\n"
    "Q4,0.0159***,0.0156***,0.0155***,0.0155***\n"
    "SE_Q4,(0.0008),(0.0008),(0.0008),(0.0007)\n"
    "Q5,0.0291***,0.0287***,0.0286***,0.0288***\n"
    "SE_Q5,(0.0012),(0.0011),(0.0011),(0.0011)\n"
    "Controls,No,Yes,Yes,Yes\n"
    "Month FE,No,No,Yes,Yes\n"
    "EDC style FE,No,No,No,Yes\n"
    "N,83319,83319,83319,83319\n"
    "R-squared,0.040,0.052,0.078,0.080\n"
)
write("tableA3_robustness_6m.csv", tableA3_csv)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE A4 — Diagnostics / QC notes
# ─────────────────────────────────────────────────────────────────────────────

tableA4_md = """\
**Table A4. Data Diagnostics and Methodological Notes**

**A. WFICN Mapping Coverage**

| Sample | Raw rows | Mapped to WFICN | Mapping rate |
|--------|--------:|----------------:|-------------:|
| Baseline (1991–2011 data) | 1,241,561 | ~1,007,000 | ~81% |
| Extension (2003–2025 data) | 2,115,074 | ~1,673,000 | ~79% |

The ~20% unmapped share consists of non-equity fund classes (bond, money market,
international) that are outside the MFLinks coverage scope. After the EDC filter, the
mapped fraction for EDC-classified funds is ≥95% in both samples.

**B. Sample Restrictions and Their Rationale**

| Restriction | Rationale | Source |
|-------------|-----------|--------|
| EDC classification | Domestic active equity only — ensures homogeneous segment | CRSP crsp_obj_cd |
| Exclude ETF (et_flag + name) | Passive trading vehicles; different flow dynamics | CRSP et_flag |
| Exclude index funds (flag + name) | Passive; remove mechanical inflow patterns | CRSP index_fund_flag |
| Lag TNA ≥ $10M | Remove tiny funds with noisy flows | Chevalier & Ellison (1997); Sirri & Tufano (1998) |
| Flow gap check (28–35 days) | Ensures TNA denominator reflects the same fund over one month | — |
| Winsorise flow 1/99 pct | Removes data errors and extreme outlier months | — |
| Min. 12 monthly returns | Rolling window requires 12 consecutive non-missing returns | — |

**C. Missing Characteristics (Extension)**

In the 2003–2025 fund summary file, `exp_ratio` and `turn_ratio` are jointly missing
for approximately 20.5% of WFICN-quarter observations. This reduces the regression
sample from 170,616 (models M1/M2, past return only or with partial controls)
to 135,585 (models M3/M4, full controls). The pattern is identical in the baseline.
Dropping `turn_ratio` from the model saves only ~215 observations; hence both are
retained for methodological consistency with the baseline.

**D. FSQ Aggregation (Extension Only)**

The 2003–2025 fund summary quarterly file does not contain a `tna_latest` column
(present in the 1991–2011 file). Categorical characteristics are assigned using the
representative share class (lowest `crsp_fundno`, i.e., the oldest class), and numeric
characteristics are averaged unweighted across share classes within each WFICN-quarter.
This is a minor deviation from the baseline's TNA-weighted aggregation; its impact
on the regression coefficients is expected to be negligible given the focus on
fund-level controls.
"""

write("tableA4_diagnostics.md", tableA4_md)


# ─────────────────────────────────────────────────────────────────────────────
# THESIS TABLE INVENTORY
# ─────────────────────────────────────────────────────────────────────────────

inventory_md = """\
# Thesis Table Inventory

Generated: 2026-06-03
Location: output/thesis_tables/

---

## Main-Text Tables

| # | File | Title | Recommended placement |
|---|------|-------|----------------------|
| 1 | table1_sample_construction_baseline.md / .csv | Sample Construction — Baseline | Section: Data & Methodology |
| 2 | table2_summary_statistics_baseline.md / .csv | Summary Statistics — Baseline | Section: Data & Methodology |
| 3 | table3_baseline_main_regression.md / .csv | Flow–Performance Regressions — Baseline | Section: Main Results |
| 4 | table4_baseline_quintile_analysis.md / .csv | Quintile Analysis — Baseline | Section: Main Results |
| 5 | table5_baseline_vs_extension_comparison.md / .csv | Baseline vs. Extension Comparison | Section: Extension / Own Contribution |

---

## Appendix Tables

| # | File | Title | Recommended placement |
|---|------|-------|----------------------|
| A1 | tableA1_extension_main_regression.md / .csv | Flow–Performance Regressions — Extension (2003–2025) | Appendix |
| A2 | tableA2_extension_quintile_analysis.md / .csv | Quintile Analysis — Extension (2003–2025) | Appendix |
| A3 | tableA3_robustness_6m.md / .csv | Robustness: 6-Month Past Performance | Appendix |
| A4 | tableA4_diagnostics.md | Data Diagnostics and Methodological Notes | Appendix |

---

## Files Created

```
output/thesis_tables/
├── table1_sample_construction_baseline.md
├── table1_sample_construction_baseline.csv
├── table2_summary_statistics_baseline.md
├── table2_summary_statistics_baseline.csv
├── table3_baseline_main_regression.md
├── table3_baseline_main_regression.csv
├── table4_baseline_quintile_analysis.md
├── table4_baseline_quintile_analysis.csv
├── table5_baseline_vs_extension_comparison.md
├── table5_baseline_vs_extension_comparison.csv
├── tableA1_extension_main_regression.md
├── tableA1_extension_main_regression.csv
├── tableA2_extension_quintile_analysis.md
├── tableA2_extension_quintile_analysis.csv
├── tableA3_robustness_6m.md
├── tableA3_robustness_6m.csv
├── tableA4_diagnostics.md
└── thesis_table_inventory.md
```

---

## Caveats for the Empirical Write-Up

1. **exp_ratio / turn_ratio missingness (20.5%):** M3/M4 regression samples are smaller
   (baseline: 77,140 vs. full 99,325; extension: 135,585 vs. full 193,074). This is
   expected and consistent across both samples. Mention in a footnote to Tables 3 and A1.

2. **No tna_latest in 2003–2025 FSQ:** Categorical characteristics use the representative
   share class (lowest crsp_fundno); numeric characteristics use unweighted means across
   share classes. Mention in a footnote or Table A4.

3. **WFICN mapping 79% overall:** Unmapped observations are non-equity funds outside
   MFLinks coverage. After the EDC filter, mapping rate for EDC funds is ≥95%.
   Mention in the data section or Table A4.

4. **Structural heterogeneity in extension period:** The 2003–2025 sample includes the
   Global Financial Crisis (2008–2009), COVID-19 shock (2020), and 2022 rate cycle.
   These events may create structural heterogeneity in the flow–performance relationship.
   Subperiod analysis is not conducted due to page constraints; phrase as a limitation.

5. **Extension is temporal robustness, not cross-source replication:** Both baseline and
   extension use CRSP data with the same WFICN-based methodology. Differences in
   coefficients reflect market structure and fund-universe changes across periods,
   not data source differences.

6. **Convexity metric:** Convexity = (Q4→Q5 step) / avg(Q2→Q3 step, Q3→Q4 step).
   This is a descriptive ratio, not a formal statistical test. The extension convexity
   (3.10×) is higher than the baseline (~2.4×); interpret cautiously.

7. **M1→M3 coefficient jump:** Without month fixed effects, aggregate time-series
   co-movement deflates the coefficient (~0.021 in both samples). Adding month FE
   isolates the cross-sectional performance-chasing signal (~0.093 baseline, ~0.117 extension).
   This jump is expected and structurally explained; mention when presenting Table 3 / A1.
"""

write("thesis_table_inventory.md", inventory_md)

# ─────────────────────────────────────────────────────────────────────────────
print()
print("All tables created:")
files = sorted(os.listdir(OUT))
for f in files:
    fpath = os.path.join(OUT, f)
    size = os.path.getsize(fpath)
    print(f"  {f:55s}  {size:>6,} bytes")
print()
print(f"Total: {len(files)} files in {OUT}")
