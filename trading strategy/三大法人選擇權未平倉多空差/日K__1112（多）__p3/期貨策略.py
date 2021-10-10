#!/usr/bin/env python
# coding: utf-8

# 匯入常用函式

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import csv
import plotly.express as px


# 連接實驗室資料庫，下sql指令撈取需要的資料



import psycopg2


#---input data---
conn = psycopg2.connect(user="islabuser1",
                        password="@islab666",
                        host="140.114.77.179",
                        port="25432",
                        database="futures_db")

sql = "SELECT table_a.date,        SUM(table_a.long_oi_volume + table_b.short_oi_volume) AS long,        SUM(table_b.long_oi_volume + table_a.short_oi_volume) AS short        FROM api_taifex_big3_options as table_a        JOIN api_taifex_big3_options as table_b        ON table_a.date=table_b.date AND table_a.type=table_b.type        WHERE table_b.long_oi_volume+table_a.short_oi_volume!=0 AND table_a.cp='c' AND table_a.cp!=table_b.cp        GROUP BY table_a.date        ORDER BY date DESC"
big3 = pd.read_sql(sql, conn)



big3.head() # big3 為每日做多跟做空的資料


# 計算多空差

big3_diff = big3.groupby(['date']).apply(lambda df: sum(df['long']) - sum(df['short']))


big3_diff = big3_diff.to_frame(name = 'longshort_diff').reset_index()

big3_diff.tail(10)
                                         

### 匯出 multichart可以讀取的csv檔

days = int(input('input the rolling day to receive longshort difference:')) 

def mc_data_diff(df,type, n):
    tmp = df.copy()
    tmp['date'] = tmp['date']
    tmp['open'] = 0
    tmp['high'] = tmp[type].apply(lambda x: x if x >= 0 else 0)
    tmp['low'] = tmp[type].apply(lambda x: x if x < 0 else 0)
    tmp['close'] = tmp[type]
    tmp['volume'] = tmp[type].rolling(n, min_periods=1).apply(lambda x: round(pd.Series(x).rank(pct=True).values[-1] * 100, 0), raw=False)
    tmp = tmp.sort_index(ascending=False).reset_index(drop=True)
    return tmp[['date', 'open', 'high', 'low', 'close', 'volume']]

threebig_mc_diff = mc_data_diff(big3_diff, 'longshort_diff', days)
threebig_mc_diff.to_csv('big3_diff_value.csv' , index=False)
