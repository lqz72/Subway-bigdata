import pandas as pd
from DataAnalysis import DataApi
from BoostModel import Predictor
from MysqlOS import SQLOS

class PredictApi(object):
    '''
    提供预测数据分析接口
    '''
    def __init__(self):
        pass

    def get_month_flow():
        '''
        单月整体的客流波动分析
        返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'month':flow,},}
        '''
        predict_results = SQLOS.get_df_data('predict')

        date_flow = predict_results[['day', 'y']]
        date_flow.day = pd.to_datetime(date_flow.day)
        date_flow.set_index('day', inplace =True)
        
        # 获取所有行程中出现的年月
        month_list = DataApi.get_month_list(date_flow.index)

        month_dict = {}
        for i in month_list:
            temp_series = date_flow.loc[i, 'y']
            day = [j.strftime("%d") for j in temp_series.index]
            flow = temp_series.values
            month_dict[i] = dict(zip(day, flow))

        return month_dict

    def get_week_flow():
        '''
        获取不同月份每周客流量 
        返回一个字典 格式{'month':{'weekday':num,},}
        '''
        predict_results = SQLOS.get_df_data('predict')

        date_flow = predict_results[['day', 'weekday', 'month', 'y']]
        date_flow.day = pd.to_datetime(date_flow.day)
        date_flow.set_index('day', inplace =True)

        # 获取所有行程中出现的年月
        month_list = DataApi.get_month_list(date_flow.index)

        week_dict = {}
        for i in month_list:
            temp_df = date_flow.loc[i, :]
            temp_dict = {}
            for weekday, flow in temp_df.groupby(by=['weekday']):
                grouped = flow.drop(labels=['weekday', 'month'], axis=1)
                mean_flow = grouped.sum() / grouped.shape[0]
                temp_dict[weekday] = int(mean_flow)
            week_dict[i] = temp_dict

        return week_dict

    def get_sta_flow(sta_name):
        '''
        单站的点出/入站客流分析
        返回两个字典 格式{'month':{'day':num,},}
        '''
        in_series, out_series = DataApi.get_sta_series(sta_name)

        in_feature_df = Predictor.get_sta_feature(in_series)
        in_predict_results = Predictor.forecast(in_feature_df, sta_name)

        out_feature_df = Predictor.get_sta_feature(out_series)
        out_predict_results = Predictor.forecast(out_feature_df, sta_name)
        
        
        def _get_month_dict(predict_results):
            date_flow = predict_results['y']

            # 获取所有行程中出现的年月
            month_list = DataApi.get_month_list(date_flow.index)

            month_dict = {}
            for i in month_list:
                temp_series = date_flow[i]
                day = [j.strftime("%d") for j in temp_series.index]
                flow = temp_series.values
                month_dict[i] = dict(zip(day, flow))

            return month_dict
        
        in_dict = _get_month_dict(in_predict_results)
        out_dict = _get_month_dict(out_predict_results) 

        return in_dict, out_dict
