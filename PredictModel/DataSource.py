# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import datetime
import os
from sys import path

class DataSource(object):
    '''
    用于对原始数据进行预处理 
    '''
    def __init__(self):
        abs_path = os.path.abspath(os.path.dirname(__file__)) + '/csv_data/'
        self.file_path = {
            'station': abs_path + 'station.csv',
            'trips': abs_path + 'trips.csv',
            'users': abs_path + 'users.csv',
            'flow': abs_path + 'flow.csv',
        }

        self.sta_df = pd.read_csv(self.file_path['station'], encoding='gb18030')
        self.trips_df = pd.read_csv(self.file_path['trips'], encoding='gb18030')
        self.age_df = pd.read_csv(self.file_path['users'], encoding='gb18030')
        
    def get_age_data(self):
        '''
        获取年龄分布 返回一个字典 {'age': amount}
        '''
        age_list = self.age_df.groupby(by="出生年份").count()["用户ID"]
        age_index = [2021 - i for i in age_list.index]
        age_values = age_list.values

        # 创建一个字典用于存放 各年龄所对应的用户人数
        age_dict = dict(zip(age_index, age_values))
        return age_dict

    def get_station_list(self):
        '''
        返回有序站点列表
        '''
        sta_list = self.sta_df["站点名称"].tolist()
        sta_list.sort(key = lambda x: int(x[3:]))
        return sta_list

    def clean_data(self):
        '''
        数据清洗 返回一个元组 存储进站和出站各自的dataframe
        '''
        #删去空缺值和重复行
        self.trips_df.dropna(axis = 0, how = 'any', inplace = True)
        self.trips_df.drop_duplicates(inplace=True)
        
        in_df = self.trips_df.loc[:,['进站名称','进站时间']]
        out_df = self.trips_df.loc[:,['出站名称','出站时间']]

        #获取站点列表
        sta_list = self.get_station_list()

        # 获取所有进站行程中出现的站点
        in_sta_list = self.trips_df["进站名称"].tolist()
        out_sta_list = self.trips_df["出站名称"].tolist()
        trips_sta_set = set(in_sta_list + out_sta_list)

        # 非法的站点名称 ['Sta104', 'Sta14', 'Sta5', 'Sta155', 'Sta98']
        ill_sta_list = list((set(sta_list) ^ trips_sta_set))

        #经验证 trips.csv中存在不存在的站点以及错误的站点名  需要删去 32583条
        index_list_in = self.trips_df[self.trips_df["进站名称"].isin(ill_sta_list)].index.tolist()
        in_df.drop(index_list_in, axis = 0, inplace = True)

        index_list_out = self.trips_df[self.trips_df["出站名称"].isin(ill_sta_list)].index.tolist()
        out_df.drop(index_list_out, axis=0, inplace=True)

        return in_df, out_df

    def get_flow_df(self):
        '''
        获取所有客流信息 即每一条进出站记录 返回一个dataframe
        dataframe格式如下  
              sta             time         day      weekday month
        0   Sta51  2019/12/26 10:07  2019-12-26         4     12
        1   Sta63  2019/12/26 10:37  2019-12-26         4     12
        2   Sta129 2019/12/26 10:42  2019-12-26         4     12
        3   Sta25  2019/12/26 11:34  2019-12-26         4     12
        4   Sta78  2019/12/26 13:10  2019-12-26         4     12

        [1517815 rows x 5 columns]
        '''
        in_df, out_df = self.clean_data()
        #创建一个新的数据表 合并进站和出站 
        in_df.columns = ['sta', 'time']
        out_df.columns = ['sta', 'time']
        flow_df = pd.concat([in_df, out_df], axis = 0)

        #增加一列 显示日期 格式：20xx-xx-xx
        flow_df['day'] = pd.to_datetime(flow_df['time']).dt.normalize()

        #增加一列 显示星期 格式：1~7 
        day_name = [1, 2, 3, 4, 5, 6, 7]
        flow_df['weekday'] = flow_df['day'].apply(lambda x: day_name[x.weekday()])

        #增加一列 显示月份 格式：1~12
        flow_df['month'] = flow_df['day'].dt.month

        #根据时间重排列
        flow_df.sort_values(by = 'time', ascending = True, inplace = True)
        flow_df.index = range(flow_df.shape[0])

        flow_df.to_csv(self.file_path['flow'], encoding='gb18030', index=0)
        return flow_df
