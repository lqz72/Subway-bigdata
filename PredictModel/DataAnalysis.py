# -*- coding: utf-8 -*-
from MysqlOS import SQLOS
import warnings
warnings.filterwarnings('ignore')

class DataApi(object):
    '''
    提供数据分析结果接口
    '''
    def __init__(self):
        self.station_list = SQLOS.get_station_list()
        self.age, self.percent = DataApi.get_age_structure()
        self.month_dict = DataApi.get_month_flow()
        self.week_dict = DataApi.get_week_flow()
        self.in_dict, self.out_dict = DataApi.get_sta_flow()

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

    def get_month_flow():
        '''
        单月整体的客流波动分析
        返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'month':flow,},}
        '''
        flow_df = SQLOS.get_flow_df()
        date_flow = DataApi.get_date_series(flow_df)

        #获取所有行程中出现的年月
        month_list = DataApi.get_month_list(date_flow.index)
        
        month_dict = day_dict = {}
        for i in month_list:
            temp_series = date_flow[i]
            day = [j.strftime("%d") for j in temp_series.index]
            flow = temp_series.values
            month_dict[i] = dict(zip(day, flow))

        print(month_dict)
        return month_dict

    def get_week_flow():
        '''
        获取不同月份每周客流量 
        返回一个字典 格式{'month':{'weekday':num,},}
        '''
        flow_df = SQLOS.get_flow_df()
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

    def get_hour_flow(df):
        '''
        获取各个站点每个小时的进站/出站客流量 
        传入一个in_df 或者 out_df 
        返回值为一个字典 格式:{'station':{'hour':num,},}
        '''
        df.columns = ['user_id', 'sta_name', 'time']
        df['flow'] = 1
  
        sta_dict = {}
        sta_list = list(set(df['sta_name'].values))
        for sta in sta_list:
            sta_df = df[df['sta_name'] == sta]
            sta_df['time'] = sta_df['time'].dt.hour

            grouped = sta_df.groupby(by = ['time'], as_index = True)['flow'].sum()
            time, flow = grouped.index, grouped.values
            sta_dict[sta] = dict(zip(time, flow))

        print(sta_dict)
        return sta_dict

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

