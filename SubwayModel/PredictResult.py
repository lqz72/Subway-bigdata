# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime
import random, math
import os

from DataAnalysis import DataApi
from PredictModel import *
from MysqlOS import SQLOS


class PredictApi(object):
    """
    提供预测数据分析接口
    """

    def __init__(self):
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.ml_predictor = MLPredictor()
        self.pred_sta_df = SQLOS.get_df_data('pred_sta_day')
        self.pred_day_df = SQLOS.get_pred_day('xgboost')
        self.pred_in_hour_df = SQLOS.get_pred_hour('in')
        self.pred_out_hour_df = SQLOS.get_pred_hour('out')
        self.pred_arima_day_df = SQLOS.get_pred_day('arima')
        self.pred_holtwinters_day_df = SQLOS.get_pred_day('holtwinters')
        self.pred_up_section_df = SQLOS.get_pred_section('up')
        self.pred_down_section_df = SQLOS.get_pred_section('down')
        self.weather_list = ["多云", "晴", "阴", "阵雨", "小雨", "中雨", "大雨", "暴雨"]
        self.line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']

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
                if os.path.exists(api.abs_path + '/xgb_model/%s.pkl' % sta):
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
        in_df = in_df.loc['2020-05-01':].drop('user_id', axis=1)
        out_df = out_df.loc['2020-05-01':].drop('user_id', axis=1)

        in_df.reset_index(level='in_time', inplace=True)
        out_df.reset_index(level='out_time', inplace=True)
        in_df['y'] = 1
        out_df['y'] = 1
        in_df['day'] = in_df.in_time.dt.normalize()
        out_df['day'] = out_df.out_time.dt.normalize()

        # in_grouped = in_df.groupby(by=['in_sta_name', 'day'], as_index=False)[['y']].sum()
        # out_grouped = out_df.groupby(by=['out_sta_name', 'day'], as_index=False)[['y']].sum()
        in_df.to_csv('./in.csv', encoding='gb18030', index=0)
        out_df.to_csv('./out.csv', encoding='gb18030', index=0)

    def time_map(self, date):
        """
        日期映射 
        """
        end = datetime.datetime.strptime(date, '%Y-%m-%d')
        start = datetime.datetime.strptime('2020-07-17', '%Y-%m-%d')
        steps = int((end - start) / pd.Timedelta(1, 'D'))

        date = start + pd.Timedelta(steps % 7, 'D')
        date = date.strftime('%Y-%m-%d')

        return date

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

    def get_sta_flow(self, sta_name):
        """
        单站的点出/入站客流分析
        返回两个字典 格式{'month':{'day':num,},}
        """
        in_series, out_series = DataApi.get_sta_series(sta_name)

        in_feature_df = self.ml_predictor.get_sta_feature(in_series)
        in_predict_results = self.ml_predictor.forecast_day_flow(in_feature_df, sta_name)

        out_feature_df = self.ml_predictor.get_sta_feature(out_series)
        out_predict_results = self.ml_predictor.forecast_day_flow(out_feature_df, sta_name)

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

    def get_curr_month_flow(self, month, **param):
        """
        获取当月客流变化
        返回一个字典 格式: {day:flow,}
        """
        alg = int(param.get('alg', 1))
        date = param.get('c_date', '2020-07-17')
        weather = self.weather_list[int(param.get('choose_wea', 2)) - 1]
        temp = int(param.get('choose_temp', 28))
        is_change = int(param.get('is_change', 0))

        if alg == 1:
            if is_change:
                self.change_pred_result(self.pred_day_df, alg=alg, date=date, weather=weather, temp=temp)

            predict_df = self.pred_day_df.copy()

        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pred_holtwinters_day_df.copy()

        month_flow = predict_df[predict_df['month'] == month]['y']

        day = [i.strftime("%d").lstrip('0') for i in month_flow.index]
        flow = month_flow.values

        return dict(zip(day, flow))

    def get_curr_week_flow(self, date, **param):
        """
        获取当前周的客流变化 
        返回一个字典 格式: {day:flow,}
        """
        alg = int(param.get('alg', 1))
        date = param.get('c_date', '2020-07-17')
        weather = self.weather_list[int(param.get('choose_wea', 2)) - 1]
        temp = int(param.get('choose_temp', 28))
        is_change = int(param.get('is_change', 0))

        if alg == 1:
            if is_change:
                self.change_pred_result(self.pred_day_df, alg=alg, date=date, weather=weather, temp=temp)

            predict_df = self.pred_day_df.copy()

        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pred_holtwinters_day_df.copy()

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

    def get_day_flow_info(self, date, **param):
        """
        获取日客流信息
        """
        alg = int(param.get('alg', 1))
        date = param.get('c_date', '2020-07-17')
        weather = self.weather_list[int(param.get('choose_wea', 2)) - 1]
        temp = int(param.get('choose_temp', 28))
        is_change = int(param.get('is_change', 0))

        if alg == 1:
            if is_change:
                self.change_pred_result(self.pred_day_df, alg=alg, date=date, weather=weather, temp=temp)

            predict_df = self.pred_day_df.copy()
            
        elif alg == 2:
            predict_df = self.pred_arima_day_df.copy()
        else:
            predict_df = self.pred_holtwinters_day_df.copy()

        std_date = pd.to_datetime(date)
        one_day = datetime.timedelta(days=1)
        pre_day = (std_date - one_day).strftime('%Y-%m-%d')
        month = date[5:7].lstrip('0')

        day_flow = int(predict_df.loc[date].y)
        pre_day_flow = int(predict_df.loc[pre_day].y)
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

        date = self.time_map(date)
        peek_hour_rate = round(self.get_peek_hour(date) / 18 * 100, 1)

        info_dict = {
            'day_flow': day_flow,
            'cmp_day': cmp_day,
            'cmp_month': cmp_month,
            'cmp_year': cmp_year,
            'am_peak_flow': am_peak_flow,
            'pm_peak_flow': pm_peak_flow,
            'peak_hour_rate': peek_hour_rate
        }
        return info_dict

    def get_day_sta_flow(self, date):
        """
        获取所有站点客流量的降序列表
        返回一个字典 格式:{station: flow}
        """
        sta_df = self.pred_sta_df.copy()
        sta_df.day = pd.to_datetime(sta_df.day)
        day_df = sta_df.set_index('day').loc[date]

        grouped = day_df.groupby(by='sta')['y'].sum()
        grouped.sort_values(ascending=False, inplace=True)

        sta_list = grouped.index
        flow_list = [(i + 1) for i in grouped.values]

        return dict(zip(sta_list, flow_list))

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

    def get_hour_flow(self, date, _type='out', line=None):
        """获取本日6-21点进出站客流

        Parameters
        ----------
        date:   有效日期
        _type:  类别 可选in, out, all
        line：  线路名称 默认为None

        Returns
        -------
        List:   列表 包含6-21小时对应的客流
        """
        if _type == 'all':
            in_pred_df = self.pred_in_hour_df[date]
            out_pred_df = self.pred_out_hour_df[date]

            if line is not None:
                sta_list = SQLOS.get_station_list(line)

                in_pred_df = in_pred_df[in_pred_df.sta.isin(sta_list)]
                out_pred_df = out_pred_df[out_pred_df.sta.isin(sta_list)]

            in_list = in_pred_df.groupby('hour')['y'].sum().values
            out_list = out_pred_df.groupby('hour')['y'].sum().values

            all_list = np.array(in_list) + np.array(out_list)
            hour_flow = [int(i) for i in all_list]
        else:
            pred_df = self.pred_in_hour_df[date] if _type == 'in' else self.pred_out_hour_df[date]

            gb = pred_df.groupby('hour')['y'].sum()

            hour_flow = [int(i) for i in gb.values]

        return hour_flow

    def get_sta_hour_flow(self, date, _type='out', station=None):
        """
        获取各个站点或指定站点6-21点的进/出站客流量 

        Parameters
        ----------
        date:    有效日期
        _type:   类别 可选in, out, all
        station: 站点名称 默认为None

        Returns
        -------
        Dict:   字典 包含6-21小时对应的客流
        """
        sta_list = SQLOS.get_station_dict().keys()
        sta_dict = dict.fromkeys(sta_list, 0)

        if _type == 'all':
            in_pred_df = self.pred_in_hour_df[date]
            out_pred_df = self.pred_out_hour_df[date]
            in_pred_df['type'] = 0
            out_pred_df['type'] = 1
            pred_df = pd.concat([in_pred_df, out_pred_df])
        else:
            pred_df = self.pred_in_hour_df[date] if _type == 'in' else self.pred_out_hour_df[date]

        if station is None:
            for sta in sta_list:
                sta_df = pred_df[pred_df['sta'].isin([sta])]

                hour_list = [i for i in range(6, 22)]
                hour_dict = dict.fromkeys(hour_list, 0)
                for hour in hour_list:
                    hour_dict[hour] = int(sta_df[sta_df.hour.isin([hour])].y.sum())
                sta_dict[sta] = hour_dict

            return sta_dict
        else:
            sta_df = pred_df[pred_df['sta'].isin([station])]

            hour_list = [i for i in range(6, 22)]
            hour_dict = dict.fromkeys(hour_list, 0)
            for hour in hour_list:
                hour_dict[hour] = int(sta_df[sta_df.hour.isin([hour])].y.sum())

            return hour_dict

    def change_pred_result(self, predict_df, **param):
        """
        判断影响因子是否修改 并重新预测
        """
        alg = param.get('alg')
        date = param.get('date')
        weather = param.get('weather')
        temp = param.get('temp')

        # 判断预测因子是否发生修改
        feature_df = self.ml_predictor.feature_day
        day_df = feature_df[feature_df['day'].isin([date])]
        default_weather = day_df.weather.values[0]
        default_temp = day_df.mean_temp.values[0]

        print(weather, default_weather)
        print(temp, int(default_temp))
        if (weather != default_weather or temp != int(default_temp)):
            """
            此时需要根据数据重新拟合 适用xgboost
            处于速度和数据量的考量 仅更新单日预测
            """
            flow = self.ml_predictor.forecast_by_factor(date=date, weather=weather, temp=temp)
            predict_df.loc[date, 'y'] = flow

        self.pred_day_df = predict_df

    def get_peek_hour(self, date):
        """
        获取每日的高峰时间
        返回持续时间 /时
        """
        try:
            hour_flow = self.get_hour_flow(date, 'all')
            hour_flow_sort = sorted(hour_flow)
            list_len = len(hour_flow)
            peek_flow = hour_flow_sort[int(list_len * 0.7) - 1]
            peek_hour = 0
            for i in range(0, list_len - 2):
                if hour_flow[i] >= peek_flow and hour_flow[i + 1] >= peek_flow and hour_flow[i + 2] >= peek_flow:
                    peek_hour += 1
            return peek_hour
        except Exception as e:
            print('Error:', e)

    def get_peek_time(self, date):
        """
        获取每日的高峰时间段
        """
        try:
            hour_flow = self.get_hour_flow(date, 'all')
            hour_flow_sort = sorted(hour_flow)
            list_len = len(hour_flow)
            peek_flow = hour_flow_sort[int(list_len * 0.8) - 1]
            peek_time = []
            for i in range(0, list_len - 1):
                if hour_flow[i] >= peek_flow and hour_flow[i + 1] >= peek_flow:
                    peek_time.append(i)
            return peek_time
        except Exception as e:
            print('Error:', e)

    def get_uneven_flow(self, date):
        """
        客流的不均衡系数
        """
        day_sta_flow = self.get_day_sta_flow(date)
        sta_flow = [i for i in day_sta_flow.values()]

        top, low = sum(sta_flow[0:5]), sum(sta_flow[-5:])

        return top / (low * 168)

    def get_flow_congestion(self, date):
        """
        交通拥挤度
        """
        line_list = self.line_list.copy()
        line_dict = {line: self.get_hour_flow(date, 'all', line) for line in line_list}

        full = 100
        count = [0] * len(line_list)
        temp_list = count.copy()

        index = 0
        for line in line_list:
            for each in line_dict[line]:
                if each >= 100:
                    temp_list[index] += each
                    count[index] += 1
            index += 1

        ratio, num = 0, 0
        for i in range(0, len(temp_list)):
            if count[i] != 0:
                ratio += temp_list[i] / (100 * count[i])
                num += 1
        ratio /= num

        return ratio

    def get_peek_flow_congestion(self, date):
        """
        高峰拥堵指数
        """
        peek_time = self.get_peek_time(date)
        line_list = self.line_list.copy()
        line_dict = {line: self.get_hour_flow(date, 'all', line) for line in line_list}

        temp_list = [0] * len(line_list)

        index = 0
        for line in line_list:
            for i in range(0, len(line_dict[line])):
                if i in peek_time:
                    temp_list[index] += line_dict[line][i]
            index += 1

        full = 100 * len(peek_time)
        ratio = sum(temp_list) / (full * len(peek_time))

        return ratio

    def get_line_capacity_ratio(self, date):
        """
        线路满载率
        """
        line_list = self.line_list.copy()
        line_dict = {line: self.get_hour_flow(date, 'all', line) for line in line_list}

        full, index = 1600, 0

        line_value = [0] * len(line_dict)

        for line in line_list:
            for i in line_dict[line]:
                line_value[index] += i
            index += 1

        ratio = sum(line_value) / (full * 8)

        return ratio

    def cal_normalized_eval(self, date):
        """
        计算归一化的五个指标
        返回一个字典或DataFrame
        """
        func_list = [
            # self.get_peek_hour,
            self.get_uneven_flow,
            self.get_flow_congestion,
            self.get_peek_flow_congestion,
            self.get_line_capacity_ratio
        ]

        eval_name = ['peek_hour', 'uneven_flow', 'flow_congestion',
                     'peek_flow_congestion', 'line_capacity_ratio']

        one_day = datetime.timedelta(days=1)

        day_list = [date]
        cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        for i in range(6):
            cur_date = cur_date + one_day
            day_list.append(cur_date.strftime('%Y-%m-%d'))

        # temp_list = []
        # for func in func_list:
        #     eval_list = []
        #     for each in day_list:
        #         eval_list.append(func(each))

        #     eval_list = np.array(eval_list)
        #     _range = np.max(eval_list) - np.min(eval_list)
        #     res = (eval_list - np.min(eval_list)) / _range

        #     temp_list.append(res)

        # day_dict = dict.fromkeys(day_list, 0)
        # i = 0
        # for day in day_list:
        #     res_list = [self.get_peek_hour(day) * 0.2]

        #     for j in range(len(func_list)):
        #         res_list.append(temp_list[j][i])

        #     day_dict[day] = dict(zip(eval_name, res_list))
        #     i += 1

        day_df = pd.DataFrame(index=day_list,
                              data=np.zeros((len(day_list), len(eval_name))), columns=eval_name)

        i = 0
        for day in day_list:
            res_list = [self.get_peek_hour(day) * 0.2]

            for func in func_list:
                eval_list = []
                for each in day_list:
                    eval_list.append(func(each))

                eval_list = np.array(eval_list)
                _range = np.max(eval_list) - np.min(eval_list)
                res = (eval_list - np.min(eval_list)) / _range

                res_list.append(res[i])

            day_df.loc[day] = res_list
            i += 1

        day_df.to_csv('./eval.csv', encoding='gb18030')

        return day_df

    def get_pre_personnel_dispatch(self, date, _type='all', station=None):
        """
        获取地铁人员调度信息
        返回一个字典
        """
        sta_flow = self.get_sta_hour_flow(date, _type, station)
        hour_personnel = {}
        for i in range(0, len(sta_flow)):
            hour_personnel[i + 6] = int(sta_flow[i + 6] * 2.5 + 2.02 + 0.06 * 15 - 0.125 * 9)

        return hour_personnel

    def get_section_flow(self, date, _type='up'):
        """
        获取断面预测客流
        返回一个字典 格式: {hour:{section:flow,},}
        """
        section_df = self.pred_up_section_df if _type == 'up' else self.pred_down_section_df
        day_df = section_df.loc[date]

        hour_list = ['7', '16']
        hour_dict = dict.fromkeys(hour_list, 0)
        for hour in hour_list:
            df = day_df[day_df.hour.isin([hour])]

            section_list = df.section.tolist()
            prediction = df.y.tolist()

            hour_dict[hour] = dict(zip(section_list, prediction))

        return hour_dict

    def get_pre_sta_score(self, date, station):
        """
        求未来的站点评分
        """
        sta_all_flow = self.get_sta_hour_flow(date, 'all')
        sta_flow = sta_all_flow[station]

        flow = 0
        for i in range(0, len(sta_flow)):
            flow += sta_flow[i + 6]
        score = 0.712 - 0.436 * math.log(flow)

        return score

    def get_pre_bicycles_num(self, date, station):
        """
        获取未来的单车投放数目
        """
        all_flow = self.get_sta_hour_flow(date, 'out')
        sta_flow = all_flow[station]
        bic_num = []
        for i in range(0, len(sta_flow)):
            if sta_flow[i + 6] <= 5:
                bic_num.append(int(sta_flow[i + 6] * 3.5) + random.randint(0, 1) + 5)
            elif sta_flow[i + 6] <= 10 and sta_flow[i + 6] > 5:
                bic_num.append(int(sta_flow[i + 6] * 3.2))
            elif sta_flow[i + 6] <= 18 and sta_flow[i + 6] > 10:
                bic_num.append(int(sta_flow[i + 6] * 2.8))
            elif sta_flow[i + 6] <= 25 and sta_flow[i + 6] > 18:
                bic_num.append(int(sta_flow[i + 6] * 2.3))
            elif sta_flow[i + 6] > 25:
                bic_num.append(int(sta_flow[i + 6] * 1.9))

        return bic_num

    def get_pre_bus_interval(self, date, station):
        """
        获取未来公交的间隔时间
        返回一个列表
        """
        all_flow = self.get_sta_hour_flow(date, 'out')
        sta_flow = all_flow[station]
        bus_interval = []
        for i in range(0, len(sta_flow)):
            if sta_flow[i + 6] <= 5:
                bus_interval.append(15 + random.randint(1, 2))
            elif sta_flow[i + 6] <= 10 and sta_flow[i + 6] > 5:
                bus_interval.append(9 + random.randint(1, 2))
            elif sta_flow[i + 6] <= 18 and sta_flow[i + 6] > 10:
                bus_interval.append(6 + random.randint(1, 2))
            elif sta_flow[i + 6] <= 25 and sta_flow[i + 6] > 18:
                bus_interval.append(4 + random.randint(1, 2))
            elif sta_flow[i + 6] > 25:
                bus_interval.append(2 + random.randint(1, 2))

        return bus_interval

    def get_pre_subway_run(self, date, station, hour):
        """
        获取预测列车运行图
        返回一个元组 分别为发车周期 横坐标列表 纵坐标列表
        """
        sta_dict = SQLOS.get_station_dict()
        line = sta_dict[station]
        sta_num = {'1号线': 22, '2号线': 24, '3号线': 46, '4号线': 8, '5号线': 10, '10号线': 22, '11号线': 31, '12号线': 18}
        line_num = sta_num[line]
        all_flow = self.get_sta_hour_flow(date, 'all')
        sta_hour_flow = all_flow[station]
        sta_flow = sta_hour_flow[hour]
        if 0 <= sta_flow < 5:
            T = 11
        elif 5 <= sta_flow < 10:
            T = 8
        elif 10 <= sta_flow < 15:
            T = 6
        elif 15 <= sta_flow < 20:
            T = 5
        elif sta_flow >= 20:
            T = 3
        x = []
        y = []
        line_num = 2 * line_num-1
        temp = -math.pi / 2
        interval = 2 * math.pi / (line_num - 1)
        for i in range(0, line_num):
            x.append(temp)
            temp += interval
        for i in range(0, len(x)):
            if i != (len(x)-1)/2 :
                y.append(math.sin(x[i]))
            else:
                y.append(1)
        flag = 0
        for i in range(1, len(x) - 1):
            pre = y[i]
            if flag == 0:
                flag = 1
                if y[i] != 1:
                    if y[i - 1] > y[i] and y[i] < y[i + 1]:
                        j = min(y[i - 1] - y[i], y[i + 1] - y[i]) - 0.1
                        if j > 0.1:
                            y[i] += random.uniform(0, j)
                    elif y[i - 1] > y[i] > y[i + 1]:
                        j = y[i - 1] - y[i] - 0.1
                        if j > 0.1:
                            y[i] += random.uniform(0, j)
                    elif y[i - 1] < y[i] < y[i + 1]:
                        j = y[i + 1] - y[i] - 0.1
                        if j > 0.1:
                            y[i] += random.uniform(0, j)
                    elif y[i - 1] < y[i] and y[i] > y[i + 1]:
                        y[i] += random.uniform(0, 0.3)
                    if y[i] >= 1 or y[i] <= -1:
                        y[i] = pre
            else:
                flag = 0
                if y[i] != 1:
                    if y[i - 1] > y[i] and y[i] < y[i + 1]:
                        y[i] -= random.uniform(0, 0.3)
                    elif y[i - 1] > y[i] > y[i + 1]:
                        j = y[i] - y[i + 1] - 0.1
                        if j > 0.1:
                            y[i] -= random.uniform(0, j)
                    elif y[i - 1] < y[i] < y[i + 1]:
                        j = y[i] - y[i - 1] - 0.1
                        if j > 0.1:
                            y[i] -= random.uniform(0, j)
                    elif y[i - 1] < y[i] and y[i] > y[i + 1]:
                        j = min(y[i] - y[i - 1], y[i] - y[i + 1]) - 0.1
                        if j > 0.1:
                            y[i] -= random.uniform(0, j)
                    if y[i] >= 1 or y[i] <= -1:
                        y[i] = pre
        xreal = [0]
        if 0 <= sta_flow < 5:
            for i in range(1, line_num + 1):
                xreal.append(i + random.randint(1, 2))
        elif 5 <= sta_flow < 10:
            for i in range(1, line_num + 1):
                xreal.append(i + random.randint(1, 2))
        elif 10 <= sta_flow < 15:
            for i in range(1, line_num + 1):
                xreal.append(i + random.randint(0, 1))
        elif 15 <= sta_flow < 20:
            for i in range(1, line_num + 1):
                xreal.append(i + random.randint(0, 1))
        elif sta_flow >= 20:
            for i in range(1, line_num + 1):
                xreal.append(i + random.randint(0, 1))
        return T, xreal, y


if __name__ == '__main__':
    pred_api = PredictApi()
    pred_api.get_pre_subway_run('2020-01-03','Sta1',11)
    # res = pred_api.get_day_sta_flow('2020-07-21')
    # print(res)
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
