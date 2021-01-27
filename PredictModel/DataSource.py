# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import os
from sys import path

class DataSource(object):
    '''
    通用数据解析类:
        用于提供数据分析所需的各种数据 
    '''
    def __init__(self):
        abs_path = os.getcwd() + '/Subway-bigdata/PredictModel/csv_data/'
        self.file_path = {
            'station': abs_path + 'station.csv',
            'trips': abs_path + 'trips.csv',
            'users': abs_path + 'users.csv',
            'workdays':abs_path + 'workdays2020.csv'
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

    def clean_data(self):
        '''
        数据清洗 返回一个元组 存储进站和出站各自的dataframe
        '''
        #删去含有空缺值的行
        if True in pd.isnull(self.trips_df):
            self.trips_df.dropna(axis = 0, how = 'any', inplace = True)

        #检验是否含有重复的行
        if True in self.trips_df.duplicated():
            #删去重复行
            self.trips_df.drop_duplicates(inplace=True)
            
        in_df = self.trips_df.loc[:,['进站名称','进站时间']]
        out_df = self.trips_df.loc[:,['出站名称','出站时间']]

        #获取站点列表
        self.sta_list = self.sta_df["站点名称"].tolist()

        # 获取所有进站行程中出现的站点
        in_sta_list = self.trips_df["进站名称"].tolist()
        out_sta_list = self.trips_df["出站名称"].tolist()
        trips_sta_set = set(in_sta_list + out_sta_list)

        # 非法的站点名称 ['Sta104', 'Sta14', 'Sta5', 'Sta155', 'Sta98']
        ill_sta_list = list((set(self.sta_list) ^ trips_sta_set))

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
                    站点             时间        day   weekday  month
        0         Sta51  2019/12/26 10:07 2019-12-26        4     12
        1         Sta63  2019/12/26 10:37 2019-12-26        4     12
        2        Sta129  2019/12/26 10:42 2019-12-26        4     12
        ...         ...               ...        ...      ...    ...
        1517813  Sta107     2020/7/9 9:59 2020-07-09        4      7
        1517814   Sta31     2020/7/9 9:59 2020-07-09        4      7

        [1517815 rows x 5 columns]
        '''
        in_df, out_df = self.clean_data()
        #创建一个新的数据表 合并进站和出站 
        temp_df_in = in_df.copy()
        temp_df_out = out_df.copy()
        temp_df_in.columns = ['站点', '时间']
        temp_df_out.columns = ['站点', '时间']
        flow_df = pd.concat([temp_df_in, temp_df_out], axis = 0)

        #增加一列 显示日期 格式：20xx-xx-xx
        flow_df['day'] = pd.to_datetime(flow_df['时间']).dt.normalize()

        #增加一列 显示星期 格式：1~7
        day_name = [1,2,3,4,5,6,7]
        flow_df['weekday'] = flow_df['day'].apply(lambda x: day_name[x.weekday()])

        #增加一列 显示月份 格式：1~12
        flow_df['month'] = flow_df['day'].dt.month

        #根据时间重排列
        flow_df.sort_values(by = '时间', ascending = True, inplace = True)
        flow_df.index = range(flow_df.shape[0])

        return flow_df

    def get_flow_data(self):
        '''
        获取时间序列对应站点的客流量 返回一个dataframe
        dataframe格式如下
                    day     站点  客流量
        0     2019-12-26    Sta1    1
        1     2019-12-26  Sta107    1
        2     2019-12-26  Sta108    2
        ...          ...     ...  ...
        30503 2020-07-16   Sta97   34
        30504 2020-07-16   Sta99  100

        [30505 rows x 3 columns]
        '''
        flow_df = self.get_flow_df()
        flow_data = flow_df.copy()
        flow_data['客流量'] = 1
        flow_data = flow_data.groupby(by=['day', '站点'], as_index=False)['客流量'].count()
        return flow_data

    @staticmethod
    def get_sta_flow(flow_data, station_name):
        '''
        提取指定站点每天的客流量 返回一个index为时间序列的series
        series格式如下
        2020-04-01     70
        2020-04-02     76
                    ... 
        2020-06-29     92
        2020-06-30     88
        '''
        tag_data = flow_data[flow_data['站点'] == station_name]
        ds = pd.Series(tag_data['客流量'].values, index = tag_data['day'].values)
        return ds

    @staticmethod
    def get_date_flow(flow_data):
        '''
        获得对应日期的总体客流量 返回一个series
        series格式如下
        2019-12-26      145
        2019-12-27      409
        2019-12-28      711
                    ...  
        2020-07-15    14390
        2020-07-16    14379
        '''
        date_flow = flow_data.groupby(by=['day'])['客流量'].sum()
        return date_flow