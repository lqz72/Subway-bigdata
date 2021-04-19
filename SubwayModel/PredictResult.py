import pandas as pd
from DataAnalysis import DataApi
from PredictModel import *
from MysqlOS import SQLOS
import datetime
import os

class PredictApi(object):
    '''
    提供预测数据分析接口
    '''
    def __init__(self):
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.ml_predictor = MLPredictor()
        self.pred_sta_df = SQLOS.get_df_data('pred_sta_day')
        self.pred_day_df = SQLOS.get_pred_day('xgboost')
        self.pred_in_hour_df = SQLOS.get_pred_hour('in')
        self.pred_out_hour_df = SQLOS.get_pred_hour('out')
        self.pred_arima_day_df = SQLOS.get_pred_day('arima')
        self.pre_holtwinters_day_df = SQLOS.get_pred_day('holtwinters')
        self.weather_list = ["多云", "晴", "阴", "阵雨", "小雨", "中雨", "大雨", "暴雨"]

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

    @staticmethod
    def get_sta_hour_feature():
        in_df, out_df = SQLOS.get_in_out_df()
        in_df = in_df.loc['2020-05-01':].drop('user_id', axis =1)
        out_df = out_df.loc['2020-05-01':].drop('user_id', axis=1)
        
        in_df.reset_index(level = 'in_time', inplace =True)
        out_df.reset_index(level = 'out_time', inplace =True)
        in_df['y'] = 1
        out_df['y'] = 1
        in_df['day'] = in_df.in_time.dt.normalize()
        out_df['day'] = out_df.out_time.dt.normalize()
        
        # in_grouped = in_df.groupby(by=['in_sta_name', 'day'], as_index=False)[['y']].sum()
        # out_grouped = out_df.groupby(by=['out_sta_name', 'day'], as_index=False)[['y']].sum()
        in_df.to_csv('./in.csv', encoding='gb18030', index=0)
        out_df.to_csv('./out.csv', encoding='gb18030', index=0)

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

    def get_curr_month_flow(self, month, **param):
        """
        获取当月客流变化
        返回一个字典 格式: {day:flow,}
        """
        alg = int(param.get('alg', 1))
        date = param.get('c_date', '2020-07-17')
        weather = self.weather_list[int(param.get('choose_wea', 2)) - 1]
        temp = int(param.get('choose_temp', 28))

        if alg == 1:
            self.change_pred_result(self.pred_day_df, alg=alg, date=date, weather=weather, temp=temp)
            
            predict_df = self.pred_day_df.copy()

        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pre_holtwinters_day_df.copy()
    
        month_flow = predict_df[predict_df['month'] == month]['y']

        day = [i.strftime("%d").lstrip('0') for i in month_flow.index]
        flow = month_flow.values

        return dict(zip(day, flow))

    def get_curr_week_flow(self, date, alg):
        """
        获取当前周的客流变化 
        返回一个字典 格式: {day:flow,}
        """
        if alg == 1:
            predict_df = self.pred_day_df.copy()
        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pre_holtwinters_day_df.copy()

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

    def get_day_flow_info(self, date, alg):
        """
        获取日客流信息
        """
        if alg == 1:
            predict_df = self.pred_day_df.copy()
        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pre_holtwinters_day_df.copy()

        std_date = pd.to_datetime(date)
        one_day = datetime.timedelta(days=1)
        pre_day = (std_date - one_day).strftime('%Y-%m-%d')
        month = date[5:7].lstrip('0')

        day_flow = int(predict_df.loc[date, 'y'])
        pre_day_flow = int(predict_df.loc[pre_day, 'y'])
        month_mean = int(predict_df[predict_df['month'] == month].y.mean())
        year_mean = int(predict_df.y.mean())

        cmp_day = round((day_flow - pre_day_flow) / pre_day_flow * 100, 1)
        cmp_month = round((day_flow - month_mean) / month_mean * 100, 1)
        cmp_year = round((day_flow - year_mean) / year_mean * 100, 1)

        in_hour_flow = self.get_hour_flow(date, 'in')
        out_hour_flow = self.get_hour_flow(date, 'out')
        am_peak_flow = 0
        pm_peak_flow = 0
        am_peak_hour = [1, 2, 3]
        pm_peak_hour = [11, 12, 13]

        if len(in_hour_flow) > 0:
            for i in am_peak_hour:
                am_peak_flow += (int(in_hour_flow[i]) + int(out_hour_flow[i]))
            for i in pm_peak_hour:
                pm_peak_flow += (int(in_hour_flow[i]) + int(out_hour_flow[i]))
        else:
            am_peak_flow = int(day_flow * 0.206)
            pm_peak_flow = int(day_flow * 0.234)

        info_dict = {
            'day_flow': day_flow,
            'cmp_day': cmp_day,
            'cmp_month': cmp_month,
            'cmp_year': cmp_year,
            'am_peak_flow': am_peak_flow,
            'pm_peak_flow': pm_peak_flow
        }
        return info_dict

    def get_line_flow_percent(self, date, sta_dict):
        """
        获取线路流量占比
        返回一个字典 {line:percent,}
        """
        line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']
        line_dict = dict.fromkeys(line_list, 0)

        df = self.pred_sta_df
        df.day = pd.to_datetime(df.day)
        df = df[df['day'].isin([date])]

        for sta in sta_dict:
            sta_df = df[df['sta'].isin([sta])]
            line_dict[sta_dict[sta]] += sta_df['y'].values[0]

        all_flow = sum(list(line_dict.values()))
        for each in line_dict:
            line_dict[each] = round(line_dict[each] / all_flow * 100, 1)

        return line_dict.keys(), line_dict.values()

    def get_hour_flow(self, date, type_ = 'out'):
        '''
        获取本日各小时进出站客流
        传入一个一个有效日期 以及进出站标识
        返回一个字典 格式:{hour:'flow'}
        '''
        pred_df = self.pred_in_hour_df[date] if type_ == 'in' else self.pred_out_hour_df[date]
        
        gb = pred_df.groupby('hour')['y'].sum()
        
        hour_flow = [str(i) for i in gb.values]

        return hour_flow

    def get_sta_hour_flow(self, date, type_ = 'out'):
        '''
        获取各个站点6-21点的进站客流量 
        传入一个一个有效日期 以及进出站标识
        返回值为一个字典 格式:{station:{hour:flow,},}
        '''
        pred_df = self.pred_in_hour_df[date] if type_== 'in' else self.pred_in_hour_df[date]
        sta_list = SQLOS.get_station_dict().keys()

        sta_dict = dict.fromkeys(sta_list, 0)
        for sta in sta_list:
            sta_df = pred_df[pred_df['sta'].isin([sta])]
            
            hour_list = [i for i in range(6,22)]
            hour_dict = dict.fromkeys(hour_list)
            for hour in hour_list:
                hour_dict[hour] = int(sta_df[sta_df.hour.isin([hour])].y.values[0])
            sta_dict[sta] = hour_dict
 
        return sta_dict

    def change_pred_result(self, predict_df, **param):
        """
        判断影响因子是否修改 并重新预测
        """
        alg = param.get('alg')
        date = param.get('date')
        weather = param.get('weather')
        temp = param.get('temp')

        #判断预测因子是否发生修改
        feature_df = self.ml_predictor.feature_day
        day_df = feature_df[feature_df['day'].isin([date])]
        default_weather = day_df.weather.values[0]
        default_temp = day_df.mean_temp.values[0]

        if (weather != default_weather or temp != int(default_temp)):
            """
            此时需要根据数据重新拟合 适用xgboost
            处于速度和数据量的考量 仅更新单日预测
            """
            flow = self.ml_predictor.forecast_by_factor(date=date, weather=weather, temp=temp)
            predict_df.loc[date, 'y'] = flow

        self.pred_day_df = predict_df

if __name__ == '__main__':
    pred_api = PredictApi()
    pred_api.get_curr_month_flow('6', c_date = '2020-07-17')
    # ml = MLPredictor()
    # rs = ml.forecast_by_factor('2020-07-17', choose_wea='阴', choose_temp='22')
    # print(rs)
    # pred_api = PredictApi()
 
    # p_api = PredictApi()
    # print(p_api.get_hour_flow('2020-07-17'))
    # p_api.get_sta_hour_flow('2020-07-17')
    # PredictApi.get_sta_hour_feature()

    # for i in range(6, 22):
    #     df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/feature/feature_out_hour/%d.csv' % i, encoding='gb18030')
    #     # df = df[df['time'] >= '2020-05-01'] 
    #     if i == 6:
    #         ddf = df
    #     else:
    #         ddf = ddf.append(df)
    # ddf.to_csv('./feature_out_hour.csv', encoding = 'gb18030', index = 0)

    # sta_list  = SQLOS.get_station_dict().keys()
    # for i in range(6, 22, 1):
    #     df = pd.read_csv(os.path.abspath(os.path.dirname(__file__)) + '/feature/feature_out_hour/%d.csv' % i, encoding='gb18030')
    #     df.time = pd.to_datetime(df.time)
    #     df = df.sort_values('time')
    #     times = list(df.time.unique())

    #     j = 0
    #     for time in times:
    #         ddf = df[df['time'] == time]
    #         real_sta_list = ddf.sta.tolist()
 
    #         nan_list  = []
    #         for sta in sta_list:
    #             if sta not in real_sta_list:
    #                 nan_list.append(sta)
    #         df_len = len(nan_list)
    #         nan_df = pd.DataFrame({'time': [time] * df_len, 'y': [0] * df_len, 'sta': nan_list})
            
    #         nan_df['time'] = pd.to_datetime(nan_df['time'])
    #         nan_df['hour'] = nan_df.time.dt.hour
    #         nan_df['weekday'] = nan_df.time.dt.weekday + 1
    #         nan_df['month'] = nan_df.time.dt.month
    #         nan_df['is_hoilday'] = ddf['is_hoilday'].values[0]
    #         nan_df['weather'] = ddf['weather'].values[0]
    #         nan_df['mean_temp'] = ddf['mean_temp'].values[0]

    #         ddf = ddf.append(nan_df)
    #         ddf = ddf.sort_values(by=['sta'], key=lambda x: x.str.lstrip('Sta').astype('int'))

        
    #         if j == 0:
    #             my_df = ddf
    #         else:
    #             my_df = my_df.append(ddf)
    #         j += 1

    #     my_df.to_csv(os.path.abspath(os.path.dirname(__file__)) + '/feature/%d.csv' % i, encoding='gb18030', index=0)
    #     print(i)

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
