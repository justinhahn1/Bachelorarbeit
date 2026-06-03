# Extension 2003–2025 — Sample Construction

## Step-by-step sample construction

| step | obs | unique_wficn | obs_removed | wficn_removed | note |
| --- | --- | --- | --- | --- | --- |
| 0. All WFICN-month observations after merge | 2115074 | 14421 |  |  |  |
| 1. Drop missing/zero portfolio_tna | 2114869 | 14421 | 205 | 0 | positive TNA required for flow |
| 2. Drop missing portfolio_return | 2060322 | 14415 | 54547 | 6 | no return available |
| 3. Keep EDC funds (crsp_obj_cd starts with 'EDC') | 280439 | 2124 | 1779883 | 12291 | broader 'ED' prefix would keep 1,073,066 obs |
| 4. Exclude ETFs (flag + name) | 253355 | 1881 | 27084 | 243 | flag: 27,012  name-based: 72 |
| 5. Exclude index funds (flag + name) | 210421 | 1612 | 42934 | 269 | flag: 41,253  name-based: 1,681 |
| 6. Exclude non-target types (international/bond/MM/balanced …) | 205420 | 1585 | 5001 | 27 | 5,001 obs caught by keywords |
| 7. Final cleaned EDC sample (before QC rules) | 205420 | 1585 |  |  |  |
| --- |  |  |  |  | Final cleaning (regression-ready): |
| 0. Step 2 input (after EDC/ETF/index filters) | 205420 | 1585 | 0 | 0 | Before final cleaning |
| 1. Drop |portfolio_return| ≥ 1 | 205418 | 1585 | 2 | 0 | economically impossible for long-only fund |
| 2. Require lag_portfolio_tna ≥ $10M | 193679 | 1474 | 11739 | 111 | Chevalier & Ellison 1997; Sirri & Tufano 1998 |
| 3. Drop missing flow_winsorized | 193074 | 1474 | 605 | 0 | DV must be non-null |
| 4. Drop remaining missing portfolio_return | 193074 | 1474 | 0 | 0 | needed for performance measures |