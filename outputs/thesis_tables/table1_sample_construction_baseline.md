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
