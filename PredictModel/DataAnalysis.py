# -*- coding: utf-8 -*-
from MysqlOS import SQLOS
from DataSource import *
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
        flow_data = DataSource.get_flow_data(flow_df)
        date_flow = DataSource.get_date_series(flow_data)

        #获取所有行程中出现的年月
        month_list = DataSource.get_month_list(date_flow.index)
        
        month_dict = day_dict = {}
        for i in month_list:
            temp_series = date_flow[i]
            day = [j.strftime("%d") for j in temp_series.index]
            flow = temp_series.values
            month_dict[i] = dict(zip(day, flow))

        return month_dict

    def get_week_flow():
        '''
        获取不同月份每周客流量 
        返回一个字典 格式{'month':{'weekday':num,},}
        '''
        flow_df = SQLOS.get_flow_df()
        flow_df['flow'] = 1 

        #获取所有行程中出现的年月
        month_list = DataSource.get_month_list(flow_df['day'])
        
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
        返回两个字典 分别存储进站和出站数据 格式{'station_name':{'month':num,},}
        '''
        in_df, out_df = SQLOS.get_trips_df()
        
        #转换为标准时间格式
        in_df.loc[:,"in_time"] = pd.to_datetime(in_df["in_time"])
        out_df.loc[:,"out_time"] = pd.to_datetime(out_df["out_time"])

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
