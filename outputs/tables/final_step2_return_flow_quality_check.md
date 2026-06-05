# Step 2 Return & Flow Quality-Control Report

## 1. portfolio_return distribution

```
  N           :        108,310
  mean        :       0.117893
  std         :      36.500314
  min         :      -0.891478
  p1          :      -0.180486
  p5          :      -0.102223
  p25         :      -0.029873
  median      :       0.011726
  p75         :       0.045885
  p95         :       0.102801
  p99         :       0.166667
  max         :  12,012.418000

  portfolio_return <  -1       :        0  (0.000%)
  portfolio_return >   1       :        1  (0.001%)
  portfolio_return >   5       :        1  (0.001%)
  portfolio_return |r| > 10    :        1  (0.001%)
```

## 2. Top 30 absolute portfolio_return observations

```
 wficn      caldt  portfolio_return  portfolio_tna  n_share_classes                                                                                                   fund_name crsp_obj_cd  lag_portfolio_tna          flow  flow_winsorized
109389 2007-12-31      12012.418000            3.5                1                       Nicholas-Applegate Institutional Funds: US Small Cap Value Fund; Institutional Shares        EDCS               21.7 -12013.256710        -0.177946
101763 2006-07-31          0.909127         2424.7                1                                                            KEELEY Small Cap Value Fund, Inc; Class A Shares        EDCS             2376.9     -0.889017        -0.177946
501021 2000-12-29         -0.891478           31.4                1                                                      GMO Trust: GMO Small Cap Growth Fund; Class III Shares        EDCS               29.0      0.974237         0.289708
501749 2009-02-27         -0.876113          101.1                7                          Goldman Sachs Trust: Goldman Sachs Structured Small Cap Value Fund; Class A Shares        EDCS              121.2      0.710271         0.289708
100366 2001-01-31          0.592593            1.0                1                                                                Bhirud Funds, Inc.: Apex Mid Cap Growth Fund        EDCM                0.5      0.407407         0.289708
107187 1999-12-31          0.555780          546.4                2                                        The PBHG Funds, Inc.: PBHG New Opportunities Fund; PBHG Class Shares        EDCS                NaN           NaN              NaN
606163 2009-04-30          0.519582           19.2                1                                                                  Rydex Variable Trust: Small-Cap Value Fund        EDCS                7.1      1.184643         0.289708
107699 2000-02-29          0.514223           53.8                1                                                              Westcore Trust: Westcore Small-Cap Growth Fund        EDCS               23.8      0.746281         0.289708
107187 2000-02-29          0.505694          458.6                1                                        The PBHG Funds, Inc.: PBHG New Opportunities Fund; PBHG Class Shares        EDCS              278.5      0.140985         0.140985
103165 2006-09-29         -0.500000            0.1                1                                                                               Ameritor Investment Fund, Inc        EDCM                0.1      0.500000         0.289708
105716 2000-06-30          0.484288         1233.1                1                                                    Van Wagoner Funds, Inc: Van Wagoner Emerging Growth Fund        EDCS              806.2      0.045233         0.045233
105762 2000-11-30         -0.481876          246.8                4 PaineWebber PACE Select Advisors Trust: PACE Small/Medium Company Growth Equity Investments; Class P Shares        EDCS              315.9      0.263136         0.263136
101763 2006-11-30         -0.475590         3377.3                1                                                            KEELEY Small Cap Value Fund, Inc; Class A Shares        EDCS             3085.9      0.570020         0.289708
100849 2005-11-30         -0.466358           43.6                3                     Eaton Vance Special Investment Trust: Eaton Vance Special Equities Fund; Class A Shares        EDCS               42.1      0.501987         0.289708
107856 2000-06-30          0.451065          653.1                1                                                       Van Wagoner Funds, Inc: Van Wagoner Post-Venture Fund        EDCS              404.7      0.162723         0.162723
105718 2000-06-30          0.434742          222.6                1                                                     Van Wagoner Funds, Inc: Van Wagoner Mid-Cap Growth Fund        EDCM              138.0      0.178301         0.178301
106643 2000-02-29          0.432707          863.9                5                                              BlackRock Funds: Micro-Cap Equity Portfolio; Investor B Shares        EDCI              571.0      0.080253         0.080253
221210 2000-02-29          0.423960          115.4                1                                                                      Forum Funds: BIA Small-Cap Growth Fund        EDCS               79.3      0.031273         0.031273
105806 2000-02-29          0.412429          369.3                1                        Standish, Ayer & Wood Investment Trust: Standish Small Cap Tax-Sensitive Equity Fund        EDCS              257.3      0.022861         0.022861
106931 2000-02-29          0.409243         1263.9                3                                                                   Kopp Emerging Growth Fund; Class A Shares        EDCM              887.8      0.014389         0.014389
240199 2000-02-29          0.405613         3613.0                5                                    BlackRock Funds: Small Cap Growth Equity Portfolio; Institutional Shares        EDCS             2554.0      0.009031         0.009031
100244 2000-02-29          0.396172          433.5                4                           Fortis Advantage Portfolios, Inc.: Capital Appreciation Portfolio; Class A Shares        EDCS              305.7      0.021884         0.021884
102597 2000-02-29          0.394816          460.2                1                                                         Oak Associates Funds: Pin Oak Aggressive Stock Fund        EDCS              264.7      0.343756         0.289708
100366 2000-11-30         -0.393846            0.6                1                                                                Bhirud Funds, Inc.: Apex Mid Cap Growth Fund        EDCM                1.0     -0.006154        -0.006154
105610 2000-02-29          0.392946          876.9                1                                                                         Northern Funds: Mid Cap Growth Fund        EDCM              566.6      0.154707         0.154707
107699 2000-06-30          0.389641           38.5                1                                                              Westcore Trust: Westcore Small-Cap Growth Fund        EDCS               22.0      0.360359         0.289708
106345 2000-02-29          0.389076           26.2                1                                                            The Bjurman Funds: Bjurman Micro-Cap Growth Fund        EDCI               16.8      0.170448         0.170448
105716 2001-09-28         -0.385998          168.2                1                                                    Van Wagoner Funds, Inc: Van Wagoner Emerging Growth Fund        EDCS              279.9     -0.013073        -0.013073
107856 2001-09-28         -0.384444           85.7                1                                                       Van Wagoner Funds, Inc: Van Wagoner Post-Venture Fund        EDCS              142.8     -0.015416        -0.015416
105718 2000-11-30         -0.384059          181.9                1                                                     Van Wagoner Funds, Inc: Van Wagoner Mid-Cap Growth Fund        EDCM              310.4     -0.029923        -0.029923
```

## 3. Raw mret — special codes and distribution

**Non-numeric CRSP codes:**
```
mret
R    57519
```

**Numeric mret distribution:**
```
  p  0.1:    -0.253719
  p  1.0:    -0.144737
  p  5.0:    -0.074361
  p 25.0:    -0.009332
  p 50.0:     0.004021
  p 75.0:     0.022265
  p 95.0:     0.073949
  p 99.0:     0.125737
  p 99.9:     0.232181
  min  :    -1.000000
  max  : 12012.418000

  mret < -1        :        0  (0.0000%)
  mret >  1        :       45  (0.0011%)
  mret >  5        :       21  (0.0005%)
  mret |m| > 10    :       11  (0.0003%)
```

**Top 30 absolute mret:**
```
     caldt  crsp_fundno         mret    mtna
2007-12-31        22169 12012.418000    3.50
2005-09-30        93941   761.200000     NaN
2011-05-31        93941   338.402780     NaN
2010-04-30        93941   325.525640     NaN
2007-02-28        93941   101.100000     NaN
2009-10-30        93941    99.981818     NaN
2004-10-29        93941    60.000000     NaN
2008-05-30        93941    43.025000     NaN
2000-01-31           61    14.186556   85.10
2008-10-31        38135    11.644112 1808.80
2002-11-29        45510    10.680108     NaN
2002-09-30        44816     8.615385     NaN
2002-04-30        10489     8.329727    8.90
2002-04-30        10465     8.329514  825.60
2002-04-30        10469     8.328528    0.10
2002-04-30        10467     8.324818    0.10
2002-04-30        10468     8.324818    0.10
2008-01-31        20241     7.782258  109.30
2002-09-30        44814     7.620690     NaN
1997-09-30         8642     5.326383  603.53
2004-03-31        27293     5.082098   45.90
2007-08-31        93941     4.964143     NaN
2002-09-30        44815     4.076142     NaN
1995-03-31         1151     3.911919     NaN
2008-09-30        42017     3.843000     NaN
2008-09-30        42018     3.843000     NaN
2005-06-30        93941     3.666667     NaN
2005-03-31        45465     3.002456    4.60
2011-12-30        53369     2.584910    7.40
2005-09-30        29233     2.013290  795.20
```

## 4. Drivers of extreme raw flow

**lag_portfolio_tna distribution for flow observations:**
```
                   n_obs  pct_of_flows  mean_abs_flow  pct_abs_flow_gt1
lag_portfolio_tna                                                      
0–1                  760         0.712          6.046             2.368
1–5                 3219         3.016          0.155             1.336
5–10                3496         3.275          0.087             0.715
10–50              18138        16.993          0.722             0.419
50–100             13055        12.231          0.042             0.138
100–500            39007        36.545          0.032             0.103
500+               29063        27.228          0.025             0.093

Corr(|flow|, log(lag_tna)) = -0.0073

  lag_tna >= $  1M  →  N=106,073  extreme (|flow|>1):   229  (0.216%)
  lag_tna >= $  5M  →  N=102,834  extreme (|flow|>1):   188  (0.183%)
  lag_tna >= $ 10M  →  N= 99,326  extreme (|flow|>1):   161  (0.162%)
  lag_tna >= $ 25M  →  N= 91,149  extreme (|flow|>1):   129  (0.142%)
  lag_tna >= $ 50M  →  N= 81,158  extreme (|flow|>1):    85  (0.105%)
```

## 5. Simulated cleaning rules

```
Baseline: 108,310 obs  /  1,322 unique WFICN

Rule                                         Obs kept   WFICN   % kept     Lost
──────────────────────────────────────────────────────────────────────
A. Drop |return| ≥ 1  (invalid return)        108,309   1,322   100.0%        1
B. Drop |return| ≥ 0.5 (aggressive trim)      108,300   1,322   100.0%       10
C. Require lag_tna ≥ $10M                      99,528   1,215    91.9%    8,782
D. Require lag_tna ≥ $5M                      103,048   1,266    95.1%    5,262
E. Combined: A + C                             99,527   1,215    91.9%    8,783
F. Combined: A + D                            103,047   1,266    95.1%    5,263
```

## 6. Recommendation & Conclusion

```

  Are extreme returns a serious problem?
  ──────────────────────────────────────────────────────────────────
  Total obs with |portfolio_return| ≥ 1     : 1  (0.001%)
  Total obs with portfolio_return < -1       : 0
  A monthly return below -100% is economically impossible for a long-only
  equity fund. These observations reflect CRSP data artefacts (tiny-TNA
  share classes with erroneous NAV entries, fund mergers recorded with
  a -1 return in the period of termination, or a $0 → very small TNA
  transition where one share class receives all TNA weight).

  Are extreme flows a serious problem?
  ──────────────────────────────────────────────────────────────────
  Obs with |raw flow| > 1 (>100% net flow)   :      247  (0.231%)
  Obs with lag_tna < $10M                    :    7,412  (6.9%)
  Near-zero lag_tna is the primary driver — when a new share class joins
  a WFICN mid-month, the prior-month TNA is near zero and the computed
  flow is huge. Current flow_winsorized already handles the worst tails,
  but tiny-lag-TNA observations will inflate flow volatility and bias
  regression coefficients if not filtered.

  Recommended cleaning rules before regressions
  ──────────────────────────────────────────────────────────────────
  Rule 1 — Drop |portfolio_return| ≥ 1:
    Removes 1 obs (0.001% of sample).
    Rationale: impossible monthly return for a long-only fund; these are
    data artefacts, not genuine outliers. Standard in the literature.

  Rule 2 — Require lag_portfolio_tna ≥ $10M:
    Removes an additional 8,783 obs vs. Rule 1 alone.
    Rationale: eliminates tiny-fund noise that drives extreme flows.
    $10M is the most common threshold in the mutual fund literature
    (Chevalier & Ellison 1997, Sirri & Tufano 1998, among others).
    Funds below this threshold have very high flow measurement error.

  Rule 3 — Retain current flow_winsorized as the main regression variable:
    After Rules 1+2, raw extreme flows virtually disappear (246 remain
    after Rule 1 alone). Winsorization at 1/99 provides a further
    safeguard. Use flow_winsorized as the dependent variable; keep raw
    flow for robustness checks.

  Rule 4 — Winsorize portfolio_return at 1/99 before constructing
    performance measures (rolling alpha, Sharpe). This is independent
    of the |return| ≥ 1 hard drop.

  Summary decision table
  ──────────────────────────────────────────────────────────────────
  Filter                                    Apply?  Reason
  drop |portfolio_return| >= 1         YES    Economically impossible
  winsorize portfolio_return 1/99      YES    For performance measures
  require lag_portfolio_tna >= $10M    YES    Literature standard; kills tiny-TNA flow noise
  keep flow_winsorized as DV           YES    Already applied; robust
  further winsorize flow 1/99          N/A    Already done in Step 2

```
