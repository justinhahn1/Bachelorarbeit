# Regression Sample Construction

## Step-by-step sample construction

| step | obs_after | wficn_after | obs_removed | wficn_removed | note |
| --- | --- | --- | --- | --- | --- |
| 0. Step 2 input | 108310 | 1322 | 0 | 0 | Before final cleaning |
| 1. Drop |portfolio_return| ≥ 1 | 108309 | 1322 | 1 | 0 | economically impossible for long-only equity fund |
| 2. Require lag_portfolio_tna ≥ $10M | 99527 | 1215 | 8782 | 107 | literature standard; removes tiny-fund flow noise |
| 3. Drop missing flow_winsorized | 99325 | 1215 | 202 | 0 | need DV for regression |
| 4. Drop remaining missing portfolio_return | 99325 | 1215 | 0 | 0 | need return for performance measures |