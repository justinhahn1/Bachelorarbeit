# Sample Construction

## Sample construction steps

| step | obs | unique_wficn | note | obs_removed | wficn_removed |
| --- | --- | --- | --- | --- | --- |
| 0. All WFICN-month observations after merge | 1241561 | 10740 |  |  |  |
| 1. Drop missing/zero portfolio_tna | 1241356 | 10740 | Requires positive TNA to compute flows | 205.0 | 0.0 |
| 2. Drop missing portfolio_return | 1163074 | 10621 | No return available for WFICN-month | 78282.0 | 119.0 |
| 3. Keep 1997-07 to 2011-12 | 971408 | 10325 | Guide-paper sample window | 191666.0 | 296.0 |
| 4. Keep EDC funds (crsp_obj_cd starts with 'EDC') | 135654 | 1653 | Also note: 'ED' prefix would keep 457,002 obs (see quality check) | 835754.0 | 8672.0 |
| 5. Exclude ETFs (flag + name) | 129782 | 1565 | Flag: 5,872  Name: 0 | 5872.0 | 88.0 |
| 6. Exclude index funds (flag + name) | 110458 | 1340 | Flag: 14,906  Name: 4,418 | 19324.0 | 225.0 |
| 7. Exclude non-target types (international/bond/MM/balanced …) | 108310 | 1322 | 2,148 obs caught by name/classification keywords | 2148.0 | 18.0 |
| 8. Final cleaned sample | 108310 | 1322 |  |  |  |