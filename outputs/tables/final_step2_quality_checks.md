# Final Step 2 — Quality Checks

## a) Top 20 WFICN-months by share-class count
```
 wficn      caldt  n_share_classes                                                                         fund_name  portfolio_tna
100247 2006-11-30               13 Hartford Mutual Funds II, Inc: Hartford Growth Opportunities Fund; Class L Shares         1271.1
100247 2006-12-29               13 Hartford Mutual Funds II, Inc: Hartford Growth Opportunities Fund; Class L Shares         1282.0
100247 2007-01-31               13 Hartford Mutual Funds II, Inc: Hartford Growth Opportunities Fund; Class L Shares         1319.7
102010 2005-03-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3845.9
102010 2005-04-29               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3637.0
102010 2005-05-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3748.4
102010 2005-06-30               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3745.9
102010 2005-07-29               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3845.2
102010 2005-08-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3703.6
102010 2005-09-30               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3707.0
102010 2005-10-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3627.9
102010 2005-11-30               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3707.5
102010 2005-12-30               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3672.2
102010 2006-01-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3804.0
102010 2006-02-28               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3668.3
102010 2006-03-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3680.6
102010 2006-04-28               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3642.8
102010 2006-05-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3283.6
102010 2006-06-30               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3230.1
102010 2006-07-31               13                     MFS Series Trust II: MFS Emerging Growth Fund; Class A Shares         3060.3
```

## b) Top 20 absolute raw flow values
```
 wficn      caldt          flow  portfolio_tna  lag_portfolio_tna                                                                                            fund_name
109389 2007-12-31 -12013.256710            3.5               21.7                Nicholas-Applegate Institutional Funds: US Small Cap Value Fund; Institutional Shares
606425 2009-12-31   1635.934492          163.7                0.1                                    JNL Series Trust: JNL/JPMorgan Midcap Growth Fund; Class A Shares
606023 2009-12-31   1397.416778          279.7                0.2                                     JNL Series Trust: JNL/Eagle SmallCap Equity Fund; Class A Shares
501527 2009-12-31    837.956315          167.8                0.2                        JNL Series Trust: JNL/Franklin Templeton Small Cap Value Fund; Class A Shares
606318 2009-12-31    463.930159           93.0                0.2                                      JNL Series Trust: JNL/AIM Small Cap Growth Fund; Class A Shares
400232 2009-12-31    104.262481           31.6                0.3                                         RidgeWorth Funds: Emerging Growth Stock Fund; Class I Shares
410899 2011-10-31     61.933680         1034.6               16.4                          Frontegra Funds, Inc: Frontegra Phocas Small Cap Value Fund; Class L Shares
400449 2010-01-29     60.203741          146.8                2.4                                Touchstone Funds Group Trust: Touchstone Mid Cap Fund; Class Z Shares
501528 2009-12-31     48.217663          280.8                5.7                               JNL Series Trust: JNL/Goldman Sachs Mid Cap Value Fund; Class A Shares
601484 2010-03-31     42.428281           60.9                1.4                                   Alger Portfolios: Alger SMidCap Growth Portfolio; Class I-2 Shares
100419 2000-02-29     42.300934           65.3                1.5 The Nottingham Investment Trust II: Brown Capital Management Small Company Fund; Institutional Class
501650 2011-08-31     38.684334         1069.2               27.0           Wells Fargo Funds Trust: Wells Fargo Advantage Emerging Growth Fund; Investor Class Shares
606428 2009-12-31     30.407447          849.4               27.0                               JNL Series Trust: JNL/T Rowe Price Mid-Cap Growth Fund; Class A Shares
601490 2009-03-31     24.762991          111.1                4.3                Sun Capital Advisers Trust: SC Goldman Sachs Mid Cap Value Fund; Initial Class Shares
107201 1999-07-30     16.590262          235.5               13.4          Salomon Brothers Series Funds, Inc.: Salomon Brothers Small Cap Growth Fund; Class B Shares
240410 2002-10-31     15.598252           18.3                1.1                                                  ProFunds: Small-Cap Growth ProFund; Investor Shares
501117 2007-05-31     15.545363          131.0                7.9                                    John Hancock Funds III: Growth Opportunities Fund; Class A Shares
501222 2009-12-31     13.843312           29.8                2.0                                           MEMBERS Mutual Funds: Small Cap Value Fund; Class Y Shares
501121 2010-01-29     12.889405            9.7                0.7                                     John Hancock Funds III: Value Opportunities Fund; Class C Shares
501166 2010-06-30     11.436334           59.4                4.8                        Virtus Equity Trust: Virtus Small-Cap Sustainable Growth Fund; Class A Shares
```

## c) ETF/index residuals in final sample
- ETF terms remaining: 0
- Index terms remaining: 0

## d) crsp_obj_cd distribution in final sample
```
crsp_obj_cd
EDCS    63940
EDCM    39048
EDCI     5322
```

## e) Date coverage by year in final sample
```
        obs  unique_wficn  pct_with_flow
year                                    
1999   5272           603           88.4
2000   6988           620           99.4
2001   7068           663           98.6
2002   7700           707           98.9
2003   8015           716           99.4
2004   8052           713           99.4
2005   8087           707           99.5
2006   8439           735           99.1
2007   8883           836           98.5
2008   9587           997           97.8
2009  10680           959           99.1
2010   9964           877           99.6
2011   9575           843           99.5
```

## f) Top 20 lipper_obj_name in final sample
```
lipper_obj_name
Small-Cap Funds    41102
Mid-Cap Funds      23922
SMALL-CAP FUNDS    22838
MID-CAP FUNDS      15117
Micro-Cap Funds     3688
MICRO-CAP FUNDS     1634
NaN                    9
```
