# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os
class Station_Flow(object):
    def __init__(self, sta_file_path, trips_file_path):
        self.sta_file_path, self.trips_file_path = sta_file_path, trips_file_path
        self.sta_df = pd.read_csv(self.sta_file_path, encoding="gb18030")
        self.trips_df = pd.read_csv(self.trips_file_path, encoding="gb18030")

    def get_ill_data(self):
        # 获取所有站点
        sta_list = self.sta_df["站点名称"].values

        # 获取所有进站行程中出现的站点
        in_sta_list = self.trips_df["进站名称"].values
        out_sta_list = self.trips_df["出站名称"].values

        # 非法的站点名称 应去除
        ill_sta_list = list(set(sta_list) ^ set(in_sta_list))
        ill_sta_list += list(set(sta_list) ^ set(out_sta_list))

        return ill_sta_list

    def process_data(self):
        ill_sta_list = self.get_ill_data()

        # 分别获取进站和出站的数据表
        in_df = self.trips_df.loc[:,["进站名称", "进站时间"]]
        out_df = self.trips_df.loc[:,["出站名称", "出站时间"]]

        in_df.loc[:,"进站时间"] = pd.to_datetime(in_df["进站时间"])
        out_df.loc[:,"出站时间"] = pd.to_datetime(out_df["出站时间"])

        #数据聚合
        in_data_dict = {}
        grouped = in_df.groupby(by="进站名称")
        for station, df_time in grouped:
            #剔除掉非法数据
            if station in ill_sta_list:
                continue
            df_time.set_index("进站时间", inplace =True)
            #数据重采样
            rs = df_time.resample("M").count()["进站名称"]
            in_time = [x.strftime('%Y-%m-%d') for x in rs.index]
            in_amount = rs.values
            in_data_dict[station] = dict(zip(in_time, in_amount))

        out_data_dict = {}
        grouped = out_df.groupby(by="出站名称")

        for station, df_time in grouped:
            df_time.set_index("出站时间", inplace =True)
            rs = df_time.resample("M").count()["出站名称"]
            out_time = [x.strftime('%Y-%m-%d') for x in rs.index]
            out_amount = rs.values
            out_data_dict[station] = dict(zip(out_time, out_amount))

        return in_data_dict, out_data_dict

# if __name__ == "__main__":
#     print(os.getcwd())
#     path1 ='./station.csv'
#     path2 = './trips.csv'
#     a = Station_Flow(path1, path2)
#     c = a.get_ill_data()
#     print(c)