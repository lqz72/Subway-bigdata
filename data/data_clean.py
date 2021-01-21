# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
station_file_path = "./station.csv"
trips_file_path = "./trips.csv"

trip_df = pd.read_csv(trips_file_path, encoding  = "gb18030")
sta_df = pd.read_csv(station_file_path, encoding  = "gb18030")

#获取所有站点
sta_list = sta_df["站点名称"].values

in_sta_list = trip_df["进站名称"].values
out_sta_list = trip_df["出站名称"].values

#非法的站点名称 应去除
ill_sta_list = list(set(sta_list) ^ set(in_sta_list))
ill_sta_list += list(set(sta_list) ^ set(out_sta_list))

in_df = trip_df.loc[:,["进站名称", "进站时间"]]
out_df = trip_df.loc[:,["出站名称", "出站时间"]]

grouped = in_df.groupby(by = "进站名称")
print(grouped["进站时间"].count())
