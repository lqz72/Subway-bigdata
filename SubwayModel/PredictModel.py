import os
import warnings

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from matplotlib import pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import (GridSearchCV, TimeSeriesSplit, cross_val_score)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBRegressor
from xgboost import plot_importance
from scipy.optimize import minimize
import seaborn as sns  
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error
from scipy.optimize import minimize  

warnings.filterwarnings('ignore')

from MysqlOS import SQLOS
from DataAnalysis import DataApi

plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei为黑体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def mean_absolute_percentage_error(y_true, y_pred):
        """平均绝对百分误差
        """
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

class MLPredictor(object):
    """机器学习预测模型
    """
    def __init__(self):
        self.abs_path = os.path.abspath(os.path.dirname(__file__))

        self.feature_day = SQLOS.get_df_data('feature_day')

        self.scaler = StandardScaler()  # 标准化缩放器

        self.tscv = TimeSeriesSplit(n_splits=5)  # 五折交叉验证

        self.xgb_best_param = {'eta': 0.3, 'n_estimators': 100, 'gamma': 0.89, 'max_depth': 7, 'min_child_weight': 1, 'colsample_bytree': 1, 'colsample_bylevel': 1, 'subsample': 
        1, 'reg_lambda': 50.0, 'reg_alpha': 5.0, 'seed': 33}

    def get_data_set(self):
        """获取数据集 时间序列单位:天

        Returns
        --------
        Dataframe: 数据集 
        columns = ['day', 'weekday', 'month', 'y', 'is_hoilday', 'weather', 'mean_temp', 'MA']
        """
        flow_df = SQLOS.get_flow_df()
        hoilday_df = SQLOS.get_df_data('hoilday2020')
        weather_df = SQLOS.get_df_data('weather2020')

        flow_df['y'] = 1
        flow_df = flow_df.groupby(by = ['day', 'weekday', 'month'], as_index = False)['y'].count()

        #选取2020/1/1之后的数据
        flow_df = flow_df[flow_df['day'] >= '2020-01-01']
        flow_df.index = range(flow_df.shape[0])
        
        #合并dataframe 并做类型转换
        weather_df.drop('day', axis=1, inplace=True)
        train_df = pd.concat([flow_df, hoilday_df.is_hoilday, weather_df], axis=1)
        train_df.dropna(inplace=True)
        train_df[['weekday', 'month', 'y']] = train_df[['weekday', 'month', 'y']].astype('int')

        #增加移动平均特征  取前3个值的平均值
        def moving_avg(x):
            return round(sum(x.values[:-1]) / (x.shape[0] - 1), 1)
        train_df['MA'] = train_df.y.rolling(4).apply(moving_avg)

        #去掉最高和最低 保留二者平均
        train_df.drop(['high_temp', 'low_temp'], axis=1, inplace=True)
        train_df.dropna(inplace=True)
                    
        return train_df

    def get_day_feature(self):
        """获取2020全年特征集 7月16日之后的MA3需填充

        Returns
        --------
        Dataframe: 特征集
        """
        feature_df = self.feature_day.copy()
        feature_df[['weekday', 'month', 'is_hoilday', 'y']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y']].astype('int')
        feature_df['MA'] = feature_df['MA'].astype('float')

        feature_df.day = pd.to_datetime(feature_df.day)
        feature_df.set_index('day', inplace=True)
        feature_df = self.feature_coding(feature_df)

        return feature_df

    def get_sta_feature(self, series):
        """获取单个站点的入站/出站客流特征集
        Parameters
        ----------
        series: 某站点入站或出站的客流series

        Returns
        --------
        Dataframe: 特征集
        """
        feature_df = self.feature_day.copy()

        #处理不符合规范的数据
        if (series.shape[0] < 198):
            nan_list = []
            day_list = [i.strftime('%Y-%m-%d') for i in series.index]

            for day in feature_df['day'].values[0:198]:
                if day not in day_list:
                    nan_list.append(day)

            nan_series = pd.Series([0] * (198 - series.shape[0]), index=nan_list)
            nan_series.index = pd.to_datetime(nan_series.index)

            series = series.append(nan_series).sort_index()

        feature_df.day = pd.to_datetime(feature_df.day)
        feature_df.set_index('day', inplace=True)
        
        feature_df.y['2020-01-01':'2020-07-16'] = series['2020-01-01':]

        def moving_avg(x):
            return round(sum(x.values[:-1]) / (x.shape[0] - 1), 1)
        feature_df['MA'] = feature_df.y.rolling(4).apply(moving_avg)

        feature_df.dropna(inplace=True)

        feature_df[['weekday', 'month', 'is_hoilday', 'y']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y']].astype('int')
        feature_df['MA'] = feature_df['MA'].astype('float')

        feature_df = self.feature_coding(feature_df)

        return feature_df

    def feature_coding(self, feature_df):
        """对特征进行编码 

        Returns
        --------
        Dataframe: 编码后的特征集
        """
        #气温信息采用label编码 
        feature_df.mean_temp = LabelEncoder().fit_transform(feature_df.mean_temp)

        #天气状况与数值无关 采用one-hot编码
        feature_df = pd.get_dummies(feature_df)

        return feature_df

    def train_test_split(self, X, y, train_size=0.9):
        """划分训练集和测试集

        Parameters
        ----------
        X: 特征集 y: 标签
        train_size: 分割比例

        Returns
        --------
        Dataframe: 特征训练集, 特征验证集, 标签训练集, 标签验证集
        """
        X_length = X.shape[0]
        split = int(X_length*train_size)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        return X_train, X_test, y_train, y_test

    def plot_model_results(self, model, X_train, X_test, y_train, y_test, plot_intervals=False, plot_anomalies=False):  
        """预测可视化 根据需求调用

        Parameters
        ----------
        model: 模型
        X_train, X_test: 特征训练集, 特征验证集
        y_train, y_test: 标签训练集, 标签验证集
        plot_intervals: 是否显示上下置信区间
        plot_anomalies：是否显示异常值
        """
        prediction = model.predict(X_test)

        plt.figure(figsize=(15, 7))
        
        plt.plot(prediction, "g", label="prediction", linewidth=2.0)
        plt.plot(y_test.values, label="actual", linewidth=2.0)

        if plot_intervals:
            cv = cross_val_score(model, X_train, y_train, cv=self.tscv, scoring="neg_mean_absolute_error")
            
            #均值
            mae = cv.mean() * (-1)

            #标准差
            deviation = cv.std()

            scale = 1.96

            #上下置信区间
            lower = prediction - (mae + scale * deviation)
            upper = prediction + (mae + scale * deviation)

            plt.plot(lower, "r--", label="upper bond / lower bond", alpha=0.5)
            plt.plot(upper, "r--", alpha=0.5)

            #异常检测
            if plot_anomalies:
                anomalies = np.array([np.NaN]*len(y_test))
                anomalies[y_test<lower] = y_test[y_test<lower]
                anomalies[y_test>upper] = y_test[y_test>upper]

                plt.plot(anomalies, "o", markersize=10, label = "Anomalies")

        #平均绝对百分误差
        error = mean_absolute_percentage_error(prediction, y_test)

        plt.title("Mean absolute percentage error {0:.2f}%".format(error))
        plt.legend(loc="best")
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(self.abs_path +'/predict.png')

    def get_xgb_best_param(self, X_train, y_train):
        """xgboost参数调优 返回最优参数字典

        Parameters
        ----------
        X_train: 训练特征集
        y_train: 训练标签集

        Returtns
        --------
        Dict: {param:value,}
        """
        other_params = {'eta': 0.3, 'n_estimators': 500, 'gamma': 0, 'max_depth': 6, 'min_child_weight': 1,
                    'colsample_bytree': 1, 'colsample_bylevel': 1, 'subsample': 1, 'reg_lambda': 1, 'reg_alpha': 0,
                    'seed': 33}

        params_dict = {
            'n_estimators':     np.linspace(100, 1000, 10, dtype=int),
            'max_depth':        np.linspace(1, 10, 10, dtype=int),
            'min_child_weight': np.linspace(1, 10, 10, dtype=int),
            'gamma':            np.linspace(0, 1, 10),
            'subsample':        np.linspace(0, 1, 11),
            'colsample_bytree': np.linspace(0, 1, 11)[1:],
            'reg_lambda':       np.linspace(0, 100, 11),
            'reg_alpha':        np.linspace(0, 10, 11),
            'learning_rate':    np.logspace(-2, 0, 10)
        }

        best_score = -0.3
        for param in params_dict:
            cv_params = {param: params_dict[param]}
    
            reg = XGBRegressor(**other_params)  #设定模型初始参数
            gs = GridSearchCV(reg, cv_params, verbose=2, refit=True, cv=5, n_jobs=-1)
            gs.fit(X_train, y_train)  # X为训练数据的特征值，y为训练数据客流量

            # 性能测评
            print("{}的最佳取值:{}".format(param, gs.best_params_[param]))
            print("最佳模型得分:", gs.best_score_)

            #更新参数字典
            if gs.best_score_ > best_score:
                best_score = gs.best_score_
                other_params[param] = gs.best_params_[param]

        self.xgb_best_params = other_params
        print('best_params: ', other_params)

        return other_params

    def fit_model(self, train_df, train_size, file_path):
        """短期时序预测 返回并保存训练好的模型

        Parameters
        ----------
        train_df: dataframe格式的数据集
        train_size: 训练集所占数据集比例

        Returtns
        --------
        Model: Xgboost回归模型
        """
        if 'day' in train_df.columns: 
            train_df.set_index('day', inplace=True)

        X, y  = train_df.drop('y', axis = 1), train_df.y
        X_train, X_test, y_train, y_test = self.train_test_split(X, y, train_size)
    
        #标准化处理
        # X_train_scaled = scaler.fit_transform(X_train)
        # X_test_scaled = scaler.transform(X_test)

        #best_param = self.
        best_param = self.xgb_best_param

        #调用xgboost回归器
        reg = XGBRegressor(**best_param)
        reg.fit(X_train, y_train)
        prediction = reg.predict(X_test)

        plot_importance(reg)

        self.plot_model_results(reg, X_train=X_train, X_test=X_test, y_train=y_train
            , y_test=y_test, plot_intervals=True)

        mae = mean_absolute_error(prediction, y_test)
        mape = mean_absolute_percentage_error(prediction, y_test)
        mse = mean_squared_error(prediction, y_test)
        r2 = r2_score(prediction, y_test)
        
        joblib.dump(reg, file_path)
        print('mae:', mae, 'mape:', mape, 'mse:', mse, 'r2_score:', r2)
        return reg

    def forecast_day_flow(self, feature_df, file_name):
        """以每一天作为时间刻度进行预测 

        Parameters
        ----------
        feature_df: dataframe格式的特征集
        file_nmae: 模型名称

        Returtns
        --------
        DataFrame index = 'day' columns = ['weekday', 'month', 'y'] 
        """
        #获取模型路径
        model_path = self.abs_path + '/model/' +  file_name + '.pkl'

        #如果模型不存在 获取训练数据拟合模型
        if os.path.exists(model_path) is False:
            #训练集只是特征集的子集 所以直接取切片即可
            train_df = feature_df['2020-01-01':'2020-07-16']

            reg = self.fit_model(train_df, 0.9, model_path)

        #调取训练模型
        model = joblib.load(model_path)

        #取7月14日之后的特征集
        feature_df = feature_df['2020-07-14':]

        moving_avg = 3
        predict_list = []
        #获取预测日期之前三天的客流量 取平均值
        for i in range(168):
            index = i + moving_avg
            feature_df.MA[index] = \
                sum(feature_df.y.values[index - moving_avg:index]) / moving_avg
            df = feature_df[index:index+1]
            X, y = df.drop(['y'], axis=1), df.y

            prediction = model.predict(X)[0]
            feature_df.y[index:index + 1] = int(prediction)
            predict_list.append(prediction)

        predict_df = feature_df.iloc[moving_avg:]
        predict_df = predict_df[['weekday', 'month', 'y']]
        
        return predict_df


class HoltWinters(object):
     
    def __init__(self, series, slen, alpha, beta, gamma, n_preds, scaling_factor=1.96):
        self.series = series
        self.slen = slen
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_preds = n_preds
        self.scaling_factor = scaling_factor

    def initial_trend(self):
        '''
        初始化趋势项
        '''
        sum = 0.0

        for i in range(self.slen):
            #计算斜率并累加
            sum += float(self.series[i+self.slen] - self.series[i]) / self.slen

        #返回平均值作为趋势项的初始值
        return sum / self.slen  

    def initial_seasonal_components(self):
        '''
        初始化季节项
        '''
        seasonals = {}
        season_averages = []
        
        #计算出周期的数目
        n_seasons = int(len(self.series)/self.slen)

        # 计算季节平均
        for j in range(n_seasons):
            season_averages.append(sum(self.series[self.slen*j:self.slen*j+self.slen])/float(self.slen))

        # 计算初始值
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen*j+i]-season_averages[j]
            seasonals[i] = sum_of_vals_over_avg / n_seasons

        return seasonals 

    def triple_exponential_smoothing(self):
        self.result = []
        self.Smooth = []
        self.Season = []
        self.Trend = []
        self.PredictedDeviation = []
        self.UpperBond = []
        self.LowerBond = []

        seasonals = self.initial_seasonal_components()

        for i in range(len(self.series)+self.n_preds):
            if i == 0: # 成分初始化
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(seasonals[i%self.slen])
                self.PredictedDeviation.append(0)
                self.UpperBond.append(self.result[0] + self.scaling_factor *  self.PredictedDeviation[0])
                self.LowerBond.append(self.result[0] - self.scaling_factor * self.PredictedDeviation[0])
                continue

            if i >= len(self.series): # 预测
                m = i - len(self.series) + 1
                self.result.append((smooth + m*trend) + seasonals[i%self.slen])

                # 预测时在每一步增加不确定性
                self.PredictedDeviation.append(self.PredictedDeviation[-1]*1.01) 
            else:
                val = self.series[i]
                last_smooth, smooth = smooth, self.alpha*(val-seasonals[i%self.slen]) + (1-self.alpha)*(smooth+trend)
                trend = self.beta * (smooth-last_smooth) + (1-self.beta)*trend
                seasonals[i%self.slen] = self.gamma*(val-smooth) + (1-self.gamma)*seasonals[i%self.slen]
                self.result.append(smooth+trend+seasonals[i%self.slen])

                # 据Brutlag算法计算偏差
                self.PredictedDeviation.append(self.gamma * np.abs(self.series[i] - self.result[i]) 
                                               + (1-self.gamma)*self.PredictedDeviation[-1])

            self.UpperBond.append(self.result[-1] + self.scaling_factor *  self.PredictedDeviation[-1])
            self.LowerBond.append(self.result[-1] - self.scaling_factor *  self.PredictedDeviation[-1])

            self.Smooth.append(smooth)
            self.Trend.append(trend)

            self.Season.append(seasonals[i%self.slen])
            
def get_data_set():
    """获取数据集 时间序列单位:天

    Returns
    --------
    Dataframe: 数据集 
    columns = ['day', 'weekday', 'month', 'y', 'is_hoilday', 'weather', 'mean_temp', 'MA']
    """
    flow_df = SQLOS.get_flow_df()
    flow_df['y'] = 1
    flow_df = flow_df.groupby(by = ['day', 'weekday', 'month'], as_index = False)['y'].count()

    #选取2020/1/1之后的数据
    flow_df = flow_df[flow_df['day'] >= '2020-01-01']
    flow_df.index = range(flow_df.shape[0])
    flow_df.drop('day', axis=1, inplace=True)
    flow_df.drop('weekday',axis=1, inplace=True)
    flow_df.drop('month',axis=1, inplace=True)
    
    return flow_df    

def timeseriesCVscore(params, series, loss_function=mean_squared_error, slen=7):
    errors = []
    values = series.values
    alpha, beta, gamma = params

    # 设定交叉验证折数
    tscv = TimeSeriesSplit(n_splits=3) 

    for train, test in tscv.split(values):
        model = HoltWinters(series=values[train], slen=slen,  alpha=alpha, beta=beta, gamma=gamma, n_preds=len(test))
        model.triple_exponential_smoothing()
        
        predictions = model.result[-len(test):]
        actual = values[test]
        
        error = loss_function(predictions, actual)
        errors.append(error)

    return np.mean(np.array(errors))
        
def plotHoltWinters(series, plot_intervals=False, plot_anomalies=False):
    """
        series - 时序数据集
        plot_intervals - 显示置信区间 
        plot_anomalies - 显示异常值 

    """
    plt.figure(figsize=(20, 10))
    plt.plot(model.result, label = "Model")
    plt.plot(series.values, label = "Actual")
    error = mean_absolute_percentage_error(series.values, model.result[:len(series)])
    plt.title("Mean Absolute Percentage Error: {0:.2f}%".format(error))

    if plot_anomalies:
        anomalies = np.array([np.NaN]*len(series))
        anomalies[series.values<model.LowerBond[:len(series)]] = series.values[series.values<model.LowerBond[:len(series)]]
        anomalies[series.values>model.UpperBond[:len(series)]] = series.values[series.values>model.UpperBond[:len(series)]]

        plt.plot(anomalies, "o", markersize=10, label = "Anomalies")

    if plot_intervals:
        plt.plot(model.UpperBond, "r--", alpha=0.5, label = "Up/Low confidence")
        plt.plot(model.LowerBond, "r--", alpha=0.5)
        plt.fill_between(x=range(0,len(model.result)), y1=model.UpperBond,y2=model.LowerBond, alpha=0.2, color = "grey")    

    plt.vlines(len(series), ymin=min(model.LowerBond), ymax=max(model.UpperBond), linestyles='dashed')
    plt.axvspan(len(series)-30, len(model.result), alpha=0.3, color='lightgrey')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc="best", fontsize=13)
    plt.savefig('./pic.png')


if __name__ == '__main__':
    pass
    # bp = MLPredictor()
    # df = bp.get_day_feature()
    # ddf = bp.forecast_day_flow(df, 'test')
    # feature_df = Predictor.get_sta_feature('Sta101')
    
    # Predictor.forecast(feature_df, 'Sta101')
    
    # flow_df=get_data_set()
    # series = pd.Series(flow_df['y'].values)
    #寻找最优的参数
    # data = series[:-30] # 留置一些数据用于测试
    # 初始化模型参数alpha、beta、gamma
    # x = [0, 0, 0]
    # 最小化损失函数
    # opt = minimize(timeseriesCVscore, x0=x,  args=(data, mean_squared_error),  method="TNC", bounds = ((0, 1), (0, 1), (0, 1)))
    # 取最优值
    # alpha_final, beta_final, gamma_final = opt.x
    # print(alpha_final, beta_final, gamma_final)
    #0.22334736563502622 0.03323882022600311 0.4090198141980643
    # model = HoltWinters(series, 7, 0.22334736563502622, 0.03323882022600311, 0.4090198141980643, 90)
    # model.triple_exponential_smoothing()  
    # plotHoltWinters(series)
