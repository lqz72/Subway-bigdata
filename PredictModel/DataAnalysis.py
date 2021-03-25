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
                                     
    def get_sta_series(sta_name):
        '''
        获取指定站点入站和出站客流的series
        '''
        in_df, out_df = SQLOS.get_trips_df()
        
        in_sta_df = in_df[in_df['in_sta_name'] == sta_name]
        out_sta_df = out_df[out_df['out_sta_name'] == sta_name]

        in_sta_df.set_index('in_time', inplace=True)
        out_sta_df.set_index('out_time', inplace=True)
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

    def get_peak_flow(df):
        '''
        获取各个站点在早晚高峰时的进/出客流
        传入一个in_df 或者 out_df
        返回两个字典 分别为早高峰(7-9)和晚高峰(5-7)时的客流量 
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

        print(am_dict)
        return am_dict, pm_dict

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

    def get_user_json():
        '''
        获取所有用户的信息 返回json文件  ##100行
        '''
        table = pd.read_csv('./PredictModel/txt_data/users.txt', encoding='gb18030')

        df = table.iloc[0:100]
        user_dict = {}

        df.columns = ['user_id', 'area', 'age', 'sex']
        print(df)
        for user_id in df.user_id.values:
            user_df = df[df['user_id'] == user_id]
            age = 2021 - int(user_df['age'].values[0])
            area = user_df['area'].values[0]
            sex = '男' if user_df['sex'].values[0] == 0 else '女'
            user_dict[user_id] = {
                'area': str(area),
                'age': str(age),
                'sex': sex,
            }
    
        with open('user_info.json', 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(user_dict, ensure_ascii=False, indent=2))
            print('success!')

    #--------------类方法---------------
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
        获取客流量前十名的站点
        返回一个列表 格式: [(station, flow, line),]
        '''
        sta_dict = self.sta_dict
        flow_df = self.flow_df
        flow_df = flow_df[flow_df['day'] == date]
        flow_df['flow'] = 1

        sta_flow = flow_df.groupby(by='sta')['flow'].sum()
        sta_flow = sta_flow.sort_values(ascending=False)

        top_sta = sta_flow.iloc[:25]
        top_sta_list = [(i, sta_dict[i], top_sta[i]) for i in top_sta.index]
        
        return top_sta_list

    def get_line_flow_percent(self, date):
        '''
        获取某日的线路流量占比 
        返回一个元组 包含线路列表和客流列表
        '''
        flow_df = self.flow_df
        sta_dict = self.sta_dict

        df = flow_df[flow_df['day'] == date]
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
        df = SQLOS.get_df_data('users')
        df = df[df['user_id'] == user_id]

        age = 2021 - int(df['birth_year'].values[0])
        area = df['area'].values[0]

        trips_df = self.trips_df
        trips_num = trips_df[trips_df['user_id'] == user_id].shape[0]

        return {'id':user_id, 'age':age, 'area':area, 'trips_num':trips_num} 

    def get_user_month_flow(self, user_id):
        '''
        获取用户每月出行次数
        返回一个字典 格式: {year-month:num,}
        '''
        df = self.trips_df

        df['in_time'] = df['in_time'].dt.normalize()
        df['out_time'] = df['out_time'].dt.normalize()
        user_trips_df = df[df['user_id'] == user_id]
        user_trips_df['flow'] = 1
       
        user_flow = user_trips_df.groupby(by='in_time')['flow'].sum()
        
        month_list = DataApi.get_month_list(user_flow.index)
        month_dict = {}
        for month in month_list:
            month_dict[month] = user_flow[month].sum()

        return month_dict

    def get_in_hour_flow(self, date):              
        '''
        获取各个站点6-21点的进站客流量 
        传入一个一个有效日期
        返回值为一个字典 格式:{station:{hour:num,},}
        '''
        df = self.in_df

        df = df.loc[date]
        df['flow'] = 1 
        df.reset_index(level='in_time', inplace=True)

        sta_hour_dict = {}
        hour_list = [str(i) for i in range(6,22)]
        sta_dict = self.sta_dict
    
        sta_hour_dict = {}
        for sta, sta_df in df.groupby(by=['in_sta_name']):
            sta_df['in_time'] = sta_df['in_time'].dt.hour.astype('str')
            grouped = sta_df.groupby(by='in_time')['flow'].sum()
     
            hour_dict = dict.fromkeys(hour_list, 0)
            for hour in grouped.index:
                hour_dict[hour] = grouped[hour]

            sta_hour_dict[sta] = hour_dict
        
        # for sta in sta_dict:
        #     hour_dict = dict.fromkeys(hour_list, 0)
        #     sta_df = df[df['in_sta_name'] == sta]

        #     sta_df['in_time'] = sta_df['in_time'].dt.hour.astype('str')
        #     sta_df = sta_df[sta_df['in_time'].isin(hour_list)]
          
        #     grouped = sta_df.groupby(by = ['in_time'], as_index = True)['flow'].sum()
            
        #     for hour in grouped.index:
        #         hour_dict[hour] = grouped[hour]
        #     sta_hour_dict[sta] = hour_dict

        return sta_hour_dict

    def get_out_hour_flow(self, date):              
        '''
        获取各个站点6-21点的出站客流量 
        传入一个一个有效日期
        返回值为一个字典 格式:{station:{hour:num,},}
        '''
        df = self.out_df

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
                hour_dict[hour] = grouped[hour]
            sta_hour_dict[sta] = hour_dict

        return sta_hour_dict

    def get_line_split(self, line, flag='up'):
        '''
        获取线路断面字典 格式: {split:0,}
        '''
        try:
            with open(self.abs_path + '/json/{}line.json'.format(flag), 'r', encoding  = 'utf-8') as f:
                line_list = json.load(f)[line]
            
                line_split = []
                for i in range(len(line_list) - 1):
                    head = line_list[i]
                    tail = line_list[i + 1]
                    line_split.append(head + '-' + tail)

                line_split_dict = dict.fromkeys(line_split, 0)

            return line_split_dict
        except Exception as e:
            print('error', e)

    def get_line_split_flow(self, date, line, flag='up'):
        '''
        获取线路断面客流 格式:{split:flow,}
        '''
        sp = ShortestPath()
        line_split = self.get_line_split(line, flag)

        trips_df = self.trips_df
        trips_df.drop('user_id', axis =1, inplace=True)
        trips_df.set_index('in_time', inplace=True)
        date_df = trips_df.loc[date]
        date_df.reset_index(level = 'in_time', inplace =True)

        for row in date_df.itertuples(index = False):
            start = getattr(row, 'in_sta_name')
            end = getattr(row, 'out_sta_name')

            path = sp.get_shortest_path(start).get(end, 0)
    
            if path != 0:
                for i in range(len(path) - 1):
                    split = path[i] + '-' + path[i + 1]
                    if split not in line_split.keys():
                        continue
                    else:
                        line_split[split] += 1

        return line_split

if __name__ == '__main__':
    pass
    # api = DataApi()
    # start = time.time()
    # a = api.get_in_hour_flow('2020-07-10')
    # end = time.time()
    # print(end - start)
    # print(a)