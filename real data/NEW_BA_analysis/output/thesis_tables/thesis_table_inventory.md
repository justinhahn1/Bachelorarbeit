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
