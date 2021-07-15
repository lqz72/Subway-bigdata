# -*- coding: utf-8 -*-
from ShortestPath import *
from MysqlOS import SQLOS
import pandas as pd
import datetime
import warnings
import json
import time
import os
warnings.filterwarnings('ignore')

class DataApi(object):
    '''
    提供数据分析结果接口
    '''
    def __init__(self):
        '''
        初始化 直接调用类属性获取数据 
        '''
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.age, self.percent = DataApi.get_age_structure()
        self.flow_df = SQLOS.get_flow_df()
        self.trips_df = SQLOS.get_trips_df()
        self.sta_dict = SQLOS.get_station_dict()
        self.month_dict = DataApi.get_month_flow(self.flow_df)
        self.date_flow = DataApi.get_date_series(self.flow_df)
        self.in_df, self.out_df = SQLOS.get_in_out_df()
        self.user_df = SQLOS.get_user_df()
    
    def get_age_structure():
        '''
        获取年龄结构 返回一个元组 分别为年龄段 和 对应的百分比
        '''
        label = ["0-20岁", "21-30岁", "31-40岁", "41—50岁", "大于50岁"]
        percent  = []
        age_dict = SQLOS.get_age_data()

        # 创建一个字典用于存放 年龄段分布
        temp_dict = dict.fromkeys(label, 0)
        for age in age_dict:
            if (0 < age) & (age <= 20):
                temp_dict["0-20岁"] += age_dict[age]
            elif (20 < age) & (age <= 30):
                temp_dict["21-30岁"] += age_dict[age]
            elif (30 < age) & (age <= 40):
                temp_dict["31-40岁"] += age_dict[age]
            elif (40 < age) & (age <= 50):
                temp_dict["41—50岁"] += age_dict[age]
            else:
                temp_dict["大于50岁"] += age_dict[age]

        all_num = sum(list(age_dict.values()))
        for val in temp_dict.values():
            percent.append(round(val * 100 / all_num, 2))

        return label, percent

    def get_month_flow(flow_df):
        '''
        单月整体的客流波动分析
        返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'day':flow,},}
        '''
        date_flow = DataApi.get_date_series(flow_df)

        #获取所有行程中出现的年月
        month_list = DataApi.get_month_list(date_flow.index)
        
        month_dict = day_dict = {}
        for i in month_list:
            temp_series = date_flow[i]
            day = [j.strftime("%d") for j in temp_series.index]
            flow = temp_series.values
            month_dict[i] = dict(zip(day, flow))
            
        return month_dict

    def get_week_flow(flow_df):
        '''
        获取不同月份每周客流量 
        返回一个字典 格式{'month':{'weekday':num,},}
        '''
        flow_df['flow'] = 1 

        #获取所有行程中出现的年月
        month_list = DataApi.get_month_list(flow_df['day'])
        
        flow_df.set_index('day', inplace=True)

        week_dict = {}
        for i in month_list:
            temp_df = flow_df.loc[i,:]
            temp_dict = {}
            for weekday, flow in temp_df.groupby(by=['weekday']):
                grouped = flow.groupby(by = ['day'])['flow'].count()
                mean_flow = grouped.sum() / grouped.shape[0]
                temp_dict[weekday] = int(mean_flow)
            week_dict[i] = temp_dict

        return week_dict

    def get_sta_flow():
        '''
        单站的点出/入站客流分析
        返回两个字典 格式{'station_name':{'month':num,},}
        '''
        in_df, out_df = SQLOS.get_trips_df()

        #重组聚合
        in_data_dict = {}
        grouped = in_df.groupby(by="in_sta_name")
        for station, df_time in grouped:
            df_time.set_index("in_time", inplace =True)
            #时间序列重采样
            rs = df_time.resample("M").count()["in_sta_name"]
            in_time = [x.strftime('%Y-%m') for x in rs.index]
            in_amount = rs.values
            in_data_dict[station] = dict(zip(in_time, in_amount))

        out_data_dict = {}
        grouped = out_df.groupby(by="out_sta_name")

        for station, df_time in grouped:
            df_time.set_index("out_time", inplace =True)
            rs = df_time.resample("M").count()["out_sta_name"]
            out_time = [x.strftime('%Y-%m') for x in rs.index]
            out_amount = rs.values
            out_data_dict[station] = dict(zip(out_time, out_amount))

        return in_data_dict, out_data_dict
                                     
    def get_sta_series(sta_name, in_flow = None, out_flow = None):
        '''
        获取指定站点入站和出站客流的series
        '''
        if in_flow is None and out_flow is None:
            in_df, out_df = SQLOS.get_in_out_df()
        else:
            in_df, out_df = in_flow, out_flow

        in_sta_df = in_df[in_df['in_sta_name'] == sta_name]
        out_sta_df = out_df[out_df['out_sta_name'] == sta_name]

        in_sta_df['y'] = out_sta_df['y'] = 1

        in_series = in_sta_df.resample('D').sum()['y']
        out_series = out_sta_df.resample('D').sum()['y']

        return in_series, out_series
    
    def get_sta_hour_series(sta_name, hour): 
        '''
        获取指定站点指定时间入站和出站客流的series 
        '''
        in_df, out_df = SQLOS.get_trips_df()
        
        in_sta_df = in_df[in_df['in_sta_name'] == sta_name]
        out_sta_df = out_df[out_df['out_sta_name'] == sta_name]
        in_sta_df['y'] = out_sta_df['y'] = 1

        in_sta_df = in_sta_df.set_index('in_time')
        out_sta_df = out_sta_df.set_index('out_time')

        in_hour_series = in_sta_df.resample('H').sum()['y']
        out_hour_series = out_sta_df.resample('H').sum()['y']

        in_series = in_hour_series.reset_index(level='in_time')
        in_series = in_series[in_series['in_time'].astype('str').str.contains('09:')]
        in_series.index = range(in_series.shape[0])
        print(in_series.y.sum())

    def get_sta_peak_flow(df, station):
        '''
        获取各个站点在早晚高峰时的进/出客流
        传入一个in_df 或者 out_df
        返回两个字典 分别为早高峰(7-9)和晚高峰(5-7)时的客流量之和
        格式: {'station':am_num}, {'station':pm_num}
        '''
        df.columns = ['user_id', 'sta_name', 'time']
        df['flow'] = 1

        sta_dict = am_dict = pm_dict = {}
        sta_list = list(set(df['sta_name'].values))
        for sta in sta_list:
            my_df = df[df['sta_name'] == sta]
            my_df['time'] = pd.to_datetime(my_df['time']).dt.hour

            grouped = my_df.groupby(by=['time'])['flow'].sum()
            am_peak, pm_peak =grouped[7:10], grouped[5:8]
            am_dict[sta], pm_dict[sta] = am_peak.sum(), pm_peak.sum()

        return am_dict, pm_dict

    def get_peak_flow(flow_df, date):
        """
        获取当天早晚高峰时的客流
        传入一个flow_df和日期date
        返回一个元组 分别为早高峰(7-9)和晚高峰(5-7)时的客流量之和
        """
        flow_df.drop(['sta', 'weekday', 'month'], axis = 1, inplace = True)
        flow_df['flow'] = 1
        date_df = flow_df[flow_df['day'].isin([date])]
        date_df['hour'] = date_df.time.dt.hour

        peak_df = date_df[date_df.hour.isin([7,8,9,17,18,19])]
        peak_df = peak_df.groupby('hour').flow.sum()

        am_peak_flow = int(peak_df[0:3].sum())
        pm_peak_flow = int(peak_df[-3:].sum())

        return am_peak_flow, pm_peak_flow

    def get_flow_data(flow_df):
        '''
        获取日期序列对应站点的客流量(入站和出站之和) 返回一个dataframe
        dataframe格式如下
                    day     sta  flow
        0     2019-12-26    Sta1    1
        1     2019-12-26  Sta107    1
        2     2019-12-26  Sta108    2
        ...          ...     ...  ...
        30503 2020-07-16   Sta97   34
        30504 2020-07-16   Sta99  100

        [30505 rows x 3 columns]
        '''
        flow_data = flow_df
        flow_data['flow'] = 1

        flow_data = flow_data.groupby(by=['day', 'sta'], as_index=False)['flow'].count()
        return flow_data
    
    def get_date_series(flow_df):
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
        flow_data = flow_df
        flow_data['flow'] = 1

        date_series = flow_data.groupby(by=['day'])['flow'].sum()
        return date_series

    def get_month_list(time_list):
        '''
        获取所有行程中出现的年月
        接收一个时间序列 返回一个有序的字符串列表
        '''
        month_list = [i.strftime("%Y-%m") for i in time_list]
        month_list = list(set(month_list))
        month_list.sort(key=lambda x: (int(x[2:4]), int(x[5:7])))
        return month_list

    def get_station_info(station):
        '''
        返回指定站点信息 
        '''
        sta_df = SQLOS.get_df_data('station')
        sta_df = sta_df[sta_df['sta_name'] == station] 

        sta_dict = {
                'line':sta_df['line'].tolist()[0], 
                'area': sta_df['area'].tolist()[0][4:]
        }
        return sta_dict


    #--------------类方法---------------
    def get_day_flow_info(self, date):
        """
        获取当前日期的客流对比信息
        返回一个字典 包含了客流对比信息和早晚高峰客流
        """
        month = date.split('-')[1]
        year = date.split('-')[0]

        am_peak_flow, pm_peak_flow = DataApi.get_peak_flow(self.flow_df.copy(), date)

        day_flow = self.date_flow[date]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        one_day = datetime.timedelta(days=1)
        pre_day_flow = self.date_flow[(date - one_day).strftime('%Y-%m-%d')]

        flow_df = self.flow_df.copy()
        flow_df.drop(['sta', 'time', 'weekday'], axis =1, inplace =True)
        flow_df['flow'] = 1
        flow_df['year'] = flow_df.day.dt.year

        year_df = flow_df[flow_df['year'] == int(year)]
        month_df = flow_df[flow_df['month'] == str(int(month))]
        year_days = int(len(year_df.day.unique()))
        month_days = int(len(month_df.day.unique()))
        year_mean = int(year_df.shape[0]) / year_days
        month_mean = int(month_df.shape[0]) / month_days

        day_cmp = round((day_flow - pre_day_flow) / pre_day_flow * 100, 1)
        month_cmp = round((day_flow - month_mean) / month_mean * 100, 1)
        year_cmp = round((day_flow - year_mean) / year_mean * 100, 1)
     
        info_dict = {
            'day_cmp':  '+{}'.format(day_cmp) if day_cmp > 0 else '{}'.format(day_cmp),
             'month_cmp': '+{}'.format(month_cmp) if month_cmp > 0 else '{}'.format(month_cmp),
             'year_cmp': '+{}'.format(year_cmp) if year_cmp > 0 else '{}'.format(year_cmp),
             'am_peak_flow': am_peak_flow,
             'pm_peak_flow': pm_peak_flow
        }

        return info_dict

    def get_curr_week_flow(self, date):
        '''
        获取当前周的客流变化 
        返回一个字典 格式: {month-day:flow,}
        '''
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        monday, sunday = date, date
        one_day = datetime.timedelta(days=1)

        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day
        # 返回当前的星期一和星期天的日期
        monday, sunday = monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')

        curr_week_flow = self.date_flow[monday:sunday]
       
        day = [j.strftime("%m-%d") for j in curr_week_flow.index]
        flow = curr_week_flow.values
        
        return dict(zip(day, flow))
   
    def get_top_sta(self, date):
        '''
        获取客流量前25名的站点
        返回一个列表 格式: [(station, line, flow),]
        '''
        sta_dict = self.sta_dict
        flow_df = self.flow_df[self.flow_df['day'] == date]
        flow_df['flow'] = 1

        sta_flow = flow_df.groupby(by='sta')['flow'].sum()
        sta_flow = sta_flow.sort_values(ascending=False)

        top_sta = sta_flow.iloc[:25]
        top_sta_list = [(i, sta_dict[i], int(top_sta[i])) for i in top_sta.index]
        
        return top_sta_list

    def get_line_flow_percent(self, date):
        '''
        获取某日的线路流量占比 
        返回一个元组 包含线路列表和客流列表
        '''
        sta_dict = self.sta_dict

        df = self.flow_df[self.flow_df['day'] == date]
        df['flow'] = 1
        df = df.groupby(by='sta', as_index=False)['flow'].sum()
        df['line'] = df.sta.apply(lambda x: sta_dict[x])

        line_series = df.groupby(by='line')['flow'].sum()
        sum_flow = line_series.sum()
        line_series = line_series.apply(lambda x: round(x / sum_flow * 100, 1))

        return line_series.index, line_series.values

    def get_user_info(self, user_id):
        '''
        获取用户信息 返回一个字典
        '''
        df = SQLOS.get_user_df()
        df = df[df['user_id'].isin([user_id])]

        age = 2021 - int(df['birth_year'].values[0])
        area = df['area'].values[0]
        category = df['category'].values[0]

        trips_df = self.trips_df
        trips_num = trips_df[trips_df['user_id'] == user_id].shape[0]

        return {'id': user_id, 'age': int(age), 'area': area, 'trips_num': int(trips_num), 'category': category}

    def get_users_by_index(self, index):
        '''
        根据索引获取某页的用户数据 偏移量15
        '''
        user_df = SQLOS.get_user_df()
        start = (index - 1) * 15
        end = start + 15

        user_list = []
        for user in user_df[start:end].itertuples(index=False):
            user_id = getattr(user, 'user_id')
            area = getattr(user, 'area')
            age = 2021 - int(getattr(user, 'birth_year'))
            sex = '男' if getattr(user, 'sex') == '0' else '女'
            
            user_list.append({
                'user_id': user_id,
                'area': area,
                'age': age,
                'sex': sex,
            })

        return user_list

    def get_user_month_flow(self, user_id):
        '''
        获取用户每月出行次数
        返回一个字典 格式: {year-month:num,}
        '''
        df = self.trips_df.copy()

        df['in_time'] = df['in_time'].dt.normalize()
        df['out_time'] = df['out_time'].dt.normalize()
        user_trips_df = df[df['user_id'].isin([user_id])]
        user_trips_df['flow'] = 1
       
        user_flow = user_trips_df.groupby(by='in_time')['flow'].sum()
        
        month_list = DataApi.get_month_list(user_flow.index)
        month_dict = {}
        for month in month_list:
            month_dict[month] = user_flow[month].sum()

        return month_dict

    def get_user_trip_record(self, user_id):
        '''
        获取单个用户出行记录
        返回一个有序列表 格式[('in_sta_name', 'in_time', 'out_sta_name', 'out_time'),]
        '''
        df = self.trips_df.copy()

        user_df = df[df['user_id'].isin([user_id])].drop('user_id', axis = 1)
        user_df = user_df.sort_values(by='in_time', ascending=True)
    
        in_sta_name, out_sta_name = user_df['in_sta_name'].values, user_df['out_sta_name'].values
        in_time = [i.strftime('%m-%d %H:%M') for i in user_df['in_time']]
        out_time = [i.strftime('%m-%d %H:%M') for i in user_df['out_time']]
        
        return list(zip(in_sta_name, in_time, out_sta_name, out_time))
        
    def get_in_hour_flow(self, date):              
        '''
        获取各个站点6-21点的进站客流量 
        传入一个一个有效日期
        返回值为一个字典 格式:{station:{hour:num,},}
        '''
        df = self.in_df.copy()

        df = df.loc[date]
        df['flow'] = 1 
        df.reset_index(level='in_time', inplace=True)

        sta_hour_dict = {}
        hour_list = [str(i) for i in range(6,22)]
        sta_dict = self.sta_dict

        for sta, sta_df in df.groupby(by=['in_sta_name']):
            sta_df['in_time'] = sta_df['in_time'].dt.hour.astype('str')
            grouped = sta_df.groupby(by='in_time')['flow'].sum()
     
            hour_dict = dict.fromkeys(hour_list, 0)
            for hour in grouped.index:
                hour_dict[hour] = int(grouped[hour])

            sta_hour_dict[sta] = hour_dict
        
        return sta_hour_dict

    def get_out_hour_flow(self, date):              
        '''
        获取各个站点6-21点的出站客流量 
        传入一个一个有效日期
        返回值为一个字典 格式:{station:{hour:num,},}
        '''
        df = self.out_df.copy()

        df = df.loc[date]
        df['flow'] = 1 
        df.reset_index(level='out_time', inplace=True)
      
        sta_hour_dict = {}
        hour_list = [str(i) for i in range(6,22)]
        sta_dict = self.sta_dict

        for sta in sta_dict:
            hour_dict = dict.fromkeys(hour_list, 0)
            sta_df = df[df['out_sta_name'] == sta]

            sta_df['out_time'] = sta_df['out_time'].dt.hour.astype('str')
            sta_df = sta_df[sta_df['out_time'].isin(hour_list)]
          
            grouped = sta_df.groupby(by = ['out_time'], as_index = True)['flow'].sum()
            
            for hour in grouped.index:
                hour_dict[hour] = int(grouped[hour])
            sta_hour_dict[sta] = hour_dict

        return sta_hour_dict

    def get_line_split(self, line, flag='up'):
        '''
        获取线路断面字典 格式: {split:0,}
        '''
        try:
            with open(self.abs_path + '/json/{}line.json'.format(flag), 'r', encoding='utf-8') as f:
                line_list = json.load(f)[line]
            
                line_split = []
                for i in range(len(line_list) - 1):
                    head = line_list[i]
                    tail = line_list[i + 1]
                    line_split.append(head + '-' + tail)

            return line_split
        except Exception as e:
            print('error', e)

    def get_line_split_flow(self, date, line):
        '''
        获取线路断面客流 格式:{split:{up:flow, down:flow},}
        '''
        sp = ShortestPath()
        #获取断面字典
        upline_split = self.get_line_split(line, flag='up')
        downline_split = self.get_line_split(line, flag='down')
        line_split_dict = {i: {'up': 0, 'down': 0} for i in upline_split} #列表分别存储上行和下行客流

        #读入出行记录
        trips_df = self.trips_df.copy().drop('user_id', axis =1)
        trips_df.set_index('in_time', inplace=True)
        date_df = trips_df.loc[date]
        date_df.reset_index(level='in_time', inplace=True)
        
        #获取所有站点到其他站点的最短路径
        all_path = {}
        for sta in self.sta_dict.keys():
            try:
                with open(self.abs_path + '/json/path/' + sta + '.json', 'r', encoding='utf-8') as f:
                    all_path[sta] = json.load(f)
            except Exception as e:
                print('error', e)

        #遍历当天的出行记录 
        for row in date_df.itertuples(index = False):
            start = getattr(row, 'in_sta_name')
            end = getattr(row, 'out_sta_name')
            
            #获取最短路径 对路径上的断面进行统计
            path = all_path[start].get(end, 0)
            if path != 0:
                for i in range(len(path) - 1):
                    split = path[i] + '-' + path[i + 1]
                    
                    if split in upline_split:
                        line_split_dict[split]['up'] += 1
                    elif split in downline_split:
                        line_split_dict[path[i + 1] + '-' + path[i]]['down'] += 1               
        
        return line_split_dict

    def get_od_flow(self, date):
        '''
        获取一个OD客流量数据
        传入一个一个有效日期
        返回值为一个字典 格式:{Sta1 :[lin1,{Sta:[line2, flow],} ],}
        '''
        #读取od站点信息
        with open(self.abs_path + '/json/sta_od.json', 'r', encoding='utf-8') as f:
            od_dict = json.load(f)
   
        #读入出行记录
        trips_df = self.trips_df.copy().drop('user_id', axis =1)
        trips_df.set_index('in_time', inplace=True)
        date_df = trips_df.loc[date]
        date_df.reset_index(level='in_time', inplace=True)

        try:
            for each in date_df.itertuples(index=False):
                in_sta = getattr(each, 'in_sta_name')
                out_sta = getattr(each, 'out_sta_name')

                if in_sta == out_sta:
                    continue

                od_dict[in_sta][1][out_sta][1] += 1
        except Exception as e:
            print(e, in_sta, out_sta)
        return od_dict

    def get_recent_weather(self, date):
        """获取近7天的完整天气信息
        """
        weather_info = SQLOS.get_df_data('weather_info')

        end_time = datetime.datetime.strptime(date, "%Y-%m-%d")  
        one_day = datetime.timedelta(days=1)
        date_list = [date,]
        for i in range(6):      
            end_time += one_day
            date_list.append(end_time.strftime("%Y-%m-%d"))
        
        recent_weather = weather_info[weather_info.date.isin(date_list)]
        weather_list = []
        for row in recent_weather.itertuples(index=False):
            weather_list.append({
                'date': getattr(row, 'date'),
                'weather': getattr(row, 'weather').split('/')[0],
                'temp': getattr(row, 'temp'),
                'wind': getattr(row, 'wind').split('/')[0]
            })

        return weather_list

    def get_sta_flow_info(self, station, date):
        """
        获取指定站点当前日期的客流对比信息
        返回一个字典 包含了客流对比信息和早晚高峰客流
        """
        month = date.split('-')[1]
        year = date.split('-')[0]

        flow_df = self.flow_df.copy()
        sta_df = flow_df[flow_df['sta'] == station]

        am_peak_flow, pm_peak_flow = DataApi.get_peak_flow(sta_df.copy(), date)
  
        sta_df['flow'] = 1
        sta_df['hour'] = sta_df.day.dt.hour
        sta_df['year'] = sta_df.day.dt.year


        day_flow = int(sta_df[sta_df.day == date].shape[0])
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        one_day = datetime.timedelta(days=1)

        pre_day_flow = int(sta_df[sta_df.day == (date - one_day).strftime('%Y-%m-%d')].shape[0])

        year_df = sta_df[sta_df['year'] == int(year)]
        month_df = sta_df[sta_df['month'] == str(int(month))]
        year_days = int(len(year_df.day.unique()))
        month_days = int(len(month_df.day.unique()))
        year_mean = int(year_df.shape[0]) / year_days
        month_mean = int(month_df.shape[0]) / month_days

        day_cmp = round((day_flow - pre_day_flow) / pre_day_flow * 100, 1)
        month_cmp = round((day_flow - month_mean) / month_mean * 100, 1)
        year_cmp = round((day_flow - year_mean) / year_mean * 100, 1)
     
        info_dict = {
            'day_cmp':  '+{}'.format(day_cmp) if day_cmp > 0 else '{}'.format(day_cmp),
            'month_cmp': '+{}'.format(month_cmp) if month_cmp > 0 else '{}'.format(month_cmp),
            'year_cmp': '+{}'.format(year_cmp) if year_cmp > 0 else '{}'.format(year_cmp),
            'am_peak_flow': am_peak_flow,
            'pm_peak_flow': pm_peak_flow
        }
        return info_dict
        
    def get_sta_curr_week_flow(self, date, station):
        '''
        获取站点当前周的客流变化 
        返回一个字典 格式: {weekday:[in_flow,out_flow],}
        '''
        weekday = datetime.datetime.strptime(date, '%Y-%m-%d')
        one_day = datetime.timedelta(days=1)

        while weekday.weekday() != 0:
            weekday -= one_day

        # 返回当前的星期一日期
        weekday_date = weekday.strftime('%Y-%m-%d')

        in_series, out_series = DataApi.get_sta_series(
            station,
            self.in_df.drop('user_id', axis = 1),
            self.out_df.drop('user_id', axis = 1)
        )

        weekday_list = ['1', '2', '3', '4', '5', '6', '7']
        curr_week_dict = dict.fromkeys(weekday_list, 0)
        in_series_date  = [i.strftime('%Y-%m-%d') for i in in_series.index]
        out_series_date = [i.strftime('%Y-%m-%d') for i in out_series.index]

        for i in range(7):
            curr_week_dict[weekday_list[i]] = [0, 0]
            if weekday_date in in_series_date:
                curr_week_dict[weekday_list[i]][0] = str(in_series.loc[weekday_date])
            else:
                curr_week_dict[weekday_list[i]][0] = "0"

            if weekday_date in out_series_date:
                curr_week_dict[weekday_list[i]][1] = str(out_series.loc[weekday_date])
            else:
                curr_week_dict[weekday_list[i]][1] = "0"
            i += 1
            weekday += one_day
            weekday_date = weekday.strftime('%Y-%m-%d')

        return curr_week_dict

    def get_sta_curr_day_flow(self, date, station):
        '''
        获取本站点6-21点的进出站客流量 
        传入一个一个有效日期
        返回值为一个字典 格式:{hour:[in_flow,out_flow],}
        '''
        def _get_data(_type):
            if _type == 'in':
                df = self.in_df.copy().drop('user_id', axis = 1)
            else:
                df = self.out_df.copy().drop('user_id', axis = 1)

            df = df[df['%s_sta_name'%_type].isin([station])]
            df = df.loc[date]
            df['flow'] = 1
            
            rs = df.resample('H')['flow'].sum()

            hours = [i.strftime('%H').lstrip('0') for i in rs.index]
            flow  = rs.values
            return dict(zip(hours, flow))

        in_dict, out_dict = _get_data('in'), _get_data('out')
   
        hour_list = [str(i) for i in range(6,22)]
        hour_dict = dict.fromkeys(hour_list, "0")

        for hour in hour_dict:
            hour_dict[hour] = [str(in_dict.get(hour, 0)), str(out_dict.get(hour, 0))]
     
        return hour_dict
    
    def get_sta_age_structure(self, date, station):
        '''
        获取出入本站的乘客年龄结构分布
        '''
        in_df, out_df = self.in_df.loc[date], self.out_df.loc[date]
        user_df = self.user_df.copy().set_index('user_id')
       
        sta_in_df = in_df[in_df['in_sta_name'].isin([station])]
        sta_out_df = out_df[out_df['out_sta_name'].isin([station])]

        sta_df = sta_in_df.append(sta_out_df)

        user_list = sta_df['user_id'].unique()

        label = ["0-20岁", "21-30岁", "31-40岁", "41—50岁", "大于50岁"]
        percent = []
        age_dict = dict.fromkeys(label, 0)
        for user in user_list:
            age = 2021 - int(user_df.loc[user].birth_year)
            if (0 < age) & (age <= 20):
                age_dict["0-20岁"] += 1
            elif (20 < age) & (age <= 30):
                age_dict["21-30岁"] += 1
            elif (30 < age) & (age <= 40):
                age_dict["31-40岁"] += 1
            elif (40 < age) & (age <= 50):
                age_dict["41—50岁"] += 1
            else:
                age_dict["大于50岁"] += 1

        all_num = sum(list(age_dict.values()))
        for val in age_dict.values():
            percent.append(round(val * 100 / all_num, 2))

        return label, percent
        
if __name__ == '__main__':
    api = DataApi()
    api.get_sta_flow_info('Sta101', '2020-07-01')
    # print(api.get_sta_age_structure('2020-07-01', 'Sta101'))

    


    
