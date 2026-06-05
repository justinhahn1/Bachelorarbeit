# Extension 2003–2025 Step 2 — Quality Checks

## a) crsp_obj_cd distribution
```
crsp_obj_cd
EDCS    119655
EDCM     77433
EDCI      8332
```

## b) ETF/index residuals
- ETF: 0
- Index: 0

## c) Flow distribution
- Raw flow N=203,174  mean=0.0937  median=-0.0054
- Winsorized bounds: [-0.1598, 0.2207]

## d) Coverage by year
```
        obs  unique_wficn  pct_with_flow
year                                    
2003   6390           699           88.8
2004   7709           700           99.0
2005   7856           691           99.5
2006   8045           716           99.0
2007   8563           837           97.7
2008   9614           999           97.8
2009  10704           956           99.2
2010   9988           878           99.6
2011   9585           843           99.5
2012   9289           808           99.4
2013   9140           804           99.3
2014   9343           808           99.2
2015   9546           820           99.4
2016   9450           830           99.2
2017   9251           800           99.4
2018   9093           782           99.4
2019   8940           770           99.7
2020   8645           742           99.9
2021   8274           711           99.9
2022   8470           860           97.8
2023   9450           820           99.7
2024   9205           799           99.7
2025   8870           773           99.8
```

## e) Top lipper_obj_name
```
lipper_obj_name
SMALL-CAP FUNDS    96726
MID-CAP FUNDS      63605
Small-Cap Funds    22929
Mid-Cap Funds      13828
MICRO-CAP FUNDS     6300
Micro-Cap Funds     2032
```

## f) Lag verification
- Corr(past_12m_return, portfolio_return) = -0.0257
- Expected near zero. PASS

## g) Baseline comparison
- Baseline N=99,325, W=1,215 (1999–2011)
- Extension N=170,616, W=1,383 (2004-04-30–2025-12-31)

## h) Coverage by year (regression sample)
```
       obs  unique_wficn  pct_r12  pct_r6
year                                     
2003  5170           617      0.0    31.2
2004  7156           630     66.8    94.9
2005  7361           650     89.0    94.0
2006  7500           676     90.4    94.3
2007  7781           746     86.4    92.1
2008  8513           764     84.5    93.3
2009  9710           876     76.3    87.3
2010  9415           827     87.9    93.8
2011  9116           801     94.3    97.1
2012  8720           756     96.1    97.8
2013  8593           756     93.1    95.8
2014  8728           757     92.8    96.2
2015  8980           773     93.2    96.3
2016  8839           768     94.7    96.9
2017  8764           762     94.7    97.4
2018  8652           749     94.8    97.2
2019  8601           744     94.8    97.2
2020  8388           725     96.1    97.8
2021  8156           697     97.6    99.1
2022  8102           736     96.1    96.7
2023  9176           787     80.4    90.8
2024  9000           772     97.4    98.7
2025  8653           743     98.1    99.1
```
