import pandas as pd
from DataAnalysis import DataApi
from PredictModel import  MLPredictor
from MysqlOS import SQLOS
import datetime
import os

class PredictApi(object):
    '''
    提供预测数据分析接口
    '''
    def __init__(self):
        self.ml_predictor = MLPredictor()
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.pred_day_df =  SQLOS.get_pred_day()

    def get_month_flow(self):
        """
        单月整体的客流波动分析
        返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'day':flow,},}
        """
        predict_results = self.pred_day_df

        date_flow = predict_results[['y']]

        # 获取所有行程中出现的年月
        month_list = DataApi.get_month_list(date_flow.index)

        month_dict = {}
        for i in month_list:
            temp_series = date_flow.loc[i, 'y']
            day = [j.strftime("%d") for j in temp_series.index]
            flow = temp_series.values
            month_dict[i] = dict(zip(day, flow))

        return month_dict

    def get_week_flow(self):
        """
        获取不同月份每周客流量 
        返回一个字典 格式{'month':{'weekday':num,},}
        """
        predict_results = self.pred_day_df

        date_flow = predict_results[['weekday', 'month', 'y']]

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

    def get_sta_flow(self,sta_name):
        """
        单站的点出/入站客流分析
        返回两个字典 格式{'month':{'day':num,},}
        """
        in_series, out_series = DataApi.get_sta_series(sta_name)

        in_feature_df =  self.ml_predictor.get_sta_feature(in_series)
        in_predict_results = self.ml_predictor.forecast_day_flow(in_feature_df, sta_name)

        out_feature_df =  self.ml_predictor.get_sta_feature(out_series)
        out_predict_results =  self.ml_predictor.forecast_day_flow(out_feature_df, sta_name)
        
        
        def get_month_dict(predict_results):
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

    def get_curr_month_flow(self, month):
        """
        获取当月客流变化
        返回一个字典 格式: {day:flow,}
        """
        predict_df = self.pred_day_df.copy()

        month_flow = predict_df[predict_df['month'] == month]['y']

        day = [i.strftime("%d").lstrip('0') for i in month_flow.index]
        flow = month_flow.values

        return dict(zip(day, flow))

    def get_curr_week_flow(self, date):
        """
        获取当前周的客流变化 
        返回一个字典 格式: {day:flow,}
        """
        predict_df = self.pred_day_df.copy()
        date_flow = predict_df['y']

        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        monday, sunday = date, date
        one_day = datetime.timedelta(days=1)

        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day
        # 返回当前的星期一和星期天的日期
        monday, sunday = monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d') 
        curr_week_flow = date_flow[monday:sunday]
       
        day = [j.strftime("%d").lstrip('0') for j in curr_week_flow.index]
        flow = curr_week_flow.values
        
        return dict(zip(day, flow))

    def get_line_flow_percent(self, date, sta_dict):
        """
        获取线路流量占比
        返回一个字典 {line:percent,}
        """
        line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']
        line_dict = dict.fromkeys(line_list, 0)

        df = SQLOS.get_df_data('pred_sta_day')
        df.day = pd.to_datetime(df.day)
        df = df[df['day'].isin([date])]

        for sta in sta_dict:
            sta_df = df[df['sta'].isin([sta])]
            line_dict[sta_dict[sta]] += sta_df['y'].values[0]

        all_flow = sum(list(line_dict.values()))
        for each in line_dict:
            line_dict[each] = round(line_dict[each] / all_flow * 100, 1)

        return line_dict.keys(), line_dict.values()

    @staticmethod
    def get_station_pred_flow():
        '''
        勿动
        对所有站点进行拟合 并输出结果到csv文件中 
        '''
        p_api = PredictApi()
        api = DataApi()
        try:
            for sta in api.sta_dict.keys():
                if os.path.exists(api.abs_path + '/model/%s.pkl' % sta):
                    continue
                in_series, out_series = DataApi.get_sta_series(sta, api.in_df, api.out_df)
                if in_series.shape[0] == 0:
                    print('0')
                    continue

                feature_df = p_api.ml_predictor.get_sta_feature(in_series)
                df = p_api.ml_predictor.forecast_day_flow(feature_df, sta)
                df.to_csv(api.abs_path + '/predict/station/%s.csv' % sta, encoding='gb18030')
            
                print(sta)
            print('success!')
        except Exception as e:
            print(in_series)
            print(e)


if __name__ == '__main__':
    for i in range(6, 22, 1):
        df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/feature/feature_per_hour/%d.csv' % i, encoding='gb18030')
        times = list(df.time.unique())
        j = 0
        for time in times:
            ddf = df[df['time'] == time]
   
            ddf = ddf.sort_values(by=['sta'], key=lambda x: x.str.lstrip('Sta').astype('int'))
            if j == 0:
                my_df = ddf
            else:
                my_df = my_df.append(ddf)
            j += 1
        my_df.to_csv(os.path.abspath(os.path.dirname(__file__)) + '/feature/%d.csv' % i, encoding='gb18030', index = 0)

    # api = DataApi()
    # p_api = PredictApi()
    # print(p_api.get_line_flow_percent(('2020-07-20'), SQLOS.get_station_dict()))
    # sta_dict = SQLOS.get_station_dict()
    # i = 0
    # for sta in sta_dict:
        
    #     sta_df = pd.read_csv(p_api.abs_path + '/predict/station/%s.csv' % sta, encoding='gb18030')
    #     sta_df['sta'] = sta
    #     if i == 0:
    #         df = sta_df
    #     else:
    #         df = df.append(sta_df)
            
    #     i += 1
    # df.index =range(df.shape[0])
    # print(df)
    # df.to_csv(p_api.abs_path + '/predict/sta.csv', index = 0, encoding = 'gb18030')
