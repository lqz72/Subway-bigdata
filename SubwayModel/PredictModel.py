import json
import os
import warnings
import joblib
import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#机器学习
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import (GridSearchCV, TimeSeriesSplit, cross_val_score)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# 统计学和计量经济学
import statsmodels.tsa.api as smt
import statsmodels.api as sm
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

class BaseModel(object):
    """基类 提供公用数据
    """
    def __init__(self):
        self.abs_path = os.path.abspath(os.path.dirname(__file__))

        self.feature_day = SQLOS.get_df_data('feature_day')

        # self.feature_in_hour = SQLOS.get_df_data('feature_in_hour')
        # self.feature_out_hour = SQLOS.get_df_data('feature_out_hour')

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

    def get_day_feature_series(self):
        """获取每日客流特征集
        Returns
        --------
        Series: 特征集
        """
        df = self.feature_day.copy()
        
        df.drop(['weekday', 'month', 'is_hoilday', 'weather', \
            'mean_temp', 'MA'], axis=1, inplace=True)
        
        df.y = df.y.astype('int')
        df.day = pd.to_datetime(df.day)
        df.index = range(df.shape[0])
        df.set_index('day', inplace=True)

        return df['y']['2020-04-01':'2020-07-16']

class MLPredictor(BaseModel):
    """机器学习预测模型
    """
    def __init__(self):
        super().__init__()

        self.tscv = TimeSeriesSplit(n_splits=5)  # 五折交叉验证

        self.xgb_best_params = {'eta': 0.36, 'n_estimators': 50, 'gamma': 0, 'max_depth': 2, 'min_child_weight': 10,
            'colsample_bytree': 1, 'colsample_bylevel': 1, 'subsample': 0.9, 'reg_lambda': 0.3, 'reg_alpha': 0.08}

        self.lgb_best_params = {'boosting_type': 'gbdt', 'objective': 'regression', 'learning_rate': 0.1, 'n_estimators': 48,
            'num_leaves': 3, 'max_depth': 3, 'min_child_samples': 18, 'min_child_weight': 0.001, 'subsample': 0.6, 'colsample_bytree': 0.6,
            'reg_alpha': 0, 'reg_lambda': 0.08}

    def get_day_feature(self):
        """获取2020全年特征集 7月16日之后的MA3需填充

        Returns
        --------
        Dataframe: 特征集
        """
        feature_df = self.feature_day.copy()
        feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']].astype('int')
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

        feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']].astype('int')
        feature_df['MA'] = feature_df['MA'].astype('float')

        feature_df = self.feature_coding(feature_df)

        return feature_df

    def get_sta_hour_feature(self, station, hour, type_ = 'in'):
        """获取单个站点的入站/出站客流特征集
        Parameters
        ----------
        station: 站点名称
        hour: 时间/时
        type_: 类型: 进站或出站

        Returns
        --------
        Dataframe: 特征集
        """
        feature_df = self.feature_in_hour.copy() if type_ == 'in' else self.feature_out_hour.copy()
        
        
        sta_df = feature_df[feature_df['sta'].isin([station])].drop('sta', axis=1)
        
        feature_df = sta_df[sta_df['hour'].isin([hour])].drop('hour', axis=1)

        feature_df.time = pd.to_datetime(feature_df.time)
        feature_df.set_index('time', inplace=True)

        # def moving_avg(x):
        #     return round(sum(x.values[:-1]) / (x.shape[0] - 1), 1)
        # feature_df['MA'] = feature_df.y.rolling(4).apply(moving_avg)

        feature_df.dropna(inplace=True)

        feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']].astype('int')
        # feature_df['MA'] = feature_df['MA'].astype('float')

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

    def train_test_split(self, X, y, train_size=0.8):
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

    def plot_model_results(self, model, file_name, X_train, X_test, y_train, y_test, plot_intervals=False, plot_anomalies=False):
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
                anomalies[y_test < lower] = y_test[y_test < lower]
                anomalies[y_test > upper] = y_test[y_test > upper]

                plt.plot(anomalies, "o", markersize=10, label = "Anomalies")

        #平均绝对百分误差
        error = mean_absolute_percentage_error(prediction, y_test)

        plt.title("Mean absolute percentage error {0:.2f}%".format(error))
        plt.legend(loc="best")
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(self.abs_path +'/{0}.png'.format(file_name))

    def get_xgb_best_param(self, X_train, y_train):
        """xgboost参数调优 返回最优参数字典

        Parameters
        ----------
        X_train: 训练特征集
        y_train: 训练标签集

        Returns
        --------
        Dict: {param:value,}
        """
        init_params = {'eta': 0.3, 'n_estimators': 500, 'gamma': 0, 'max_depth': 6, 'min_child_weight': 1,
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
    
            reg = XGBRegressor(**init_params)  # 设定模型初始参数
            gscv = GridSearchCV(reg, cv_params, verbose=2, refit=True, cv=5, n_jobs=-1)
            gscv.fit(X_train, y_train)  # X为训练数据的特征值，y为训练数据客流量

            # 性能测评
            print("{}的最佳取值:{}".format(param, gscv.best_params_[param]))
            print("最佳模型得分:", gscv.best_score_)

            #更新参数字典
            if gscv.best_score_ > best_score:
                best_score = gscv.best_score_
                init_params[param] = gscv.best_params_[param]

        self.xgb_best_params = init_params
        print('best_params: ', init_params)

        return init_params

    def get_lgb_best_param(self, X_train, y_train):
        """lightgbm参数调优 返回最优参数字典
        Parameters
        ----------
        X_train: 训练特征集
        y_train: 训练标签集

        Returns
        --------
        Dict: {param:value,}
        """
        init_params = {'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 200, 'objective': 'multiclass', 'num_class': 3,
                    'booster': 'gbtree', 'min_child_weight': 2, 'subsample': 0.8, 'colsample_bytree': 0.8, 'reg_alpha': 0,
                    'reg_lambda': 1, 'seed': 0}

        params_dict = {
            'max_depth': [15, 20, 25, 30, 35],
            'learning_rate': [0.01, 0.02, 0.05, 0.1, 0.15],
            'feature_fraction': [0.6, 0.7, 0.8, 0.9, 0.95],
            'bagging_fraction': [0.6, 0.7, 0.8, 0.9, 0.95],
            'bagging_freq': [2, 4, 5, 6, 8],
            'lambda_l1': [0, 0.1, 0.4, 0.5, 0.6],
            'lambda_l2': [0, 10, 15, 35, 40],
            'cat_smooth': [1, 10, 15, 20, 35]
        }
        gbm = LGBMRegressor(**init_params)

        gscv = GridSearchCV(gbm, param_grid=params_dict, scoring='accuracy', cv=5)
        gscv.fit(X_train, y_train)
        print("Best score: %0.3f" % gscv.best_score_)
        print("Best parameters set:")
        best_parameters = gscv.best_estimator_.get_params()
        for param_name in sorted(params_dict.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))

    def fit_model(self, model, train_df, train_size, file_path):
        """短期时序预测 返回并保存训练好的模型

        Parameters
        ----------
        train_df: dataframe格式的数据集
        train_size: 训练集所占数据集比例

        Returns
        --------
        Model: Xgboost回归模型
        MAPE: 平均绝对百分误差
        """
        if 'day' in train_df.columns: 
            train_df.set_index('day', inplace=True)

        X, y = train_df.drop('y', axis=1), train_df.y
        X_train, X_test, y_train, y_test = self.train_test_split(X, y, train_size)

        #调用模型
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_pred, y_test)
        mape = mean_absolute_percentage_error(y_pred, y_test)
        mse = mean_squared_error(y_pred, y_test)
        r2 = r2_score(y_pred, y_test)
        
        joblib.dump(model, file_path)
        print('mae:', mae, 'mape:', mape, 'mse:', mse, 'r2_score:', r2)
        return model, mape

    def model_ensemble(self, feature_df, file_name, n_steps=168):
        """基于blending进行模型融合

        Parameters
        ----------
        feature_df: dataframe格式的特征集
        file_name: 文件名称
        n_steps:   预测步长

        Returns
        --------
        DataFrame  预测结果
        """
        df, y_xgb, mape_xgb = self.forecast_day_flow('xgb', feature_df, file_name, n_steps)
        df, y_lgb, mape_lgb = self.forecast_day_flow('lgb', feature_df, file_name, n_steps)

        # XGBoost和lightgbm模型融合
        weight_xgb = mape_xgb / (mape_xgb + mape_lgb)
        weight_lgb = mape_lgb / (mape_xgb + mape_lgb)

        prediction = (y_xgb ** weight_xgb) * (y_lgb ** weight_lgb)
        
        datetime.datetime.strptime
        start_time =datetime.datetime.strptime('2020-07-17', '%Y-%m-%d')
        end_time = start_time + datetime.timedelta(days=n_steps-1)
        str_time = end_time.strftime('%Y-%m-%d')

        df['2020-07-17': str_time].y = prediction

        return df

    def get_fitted_model(self, model_name, feature_df, file_name, start_time):
        """获取拟合过的预测模型
        如果该模型已经训练过，直接调用 否则需要训练后保存

        Parameters
        ----------
        model_name:  模型名称
        feature_df:  dataframe格式的特征集
        file_name:  文件名称
        start_time: 训练集起始时间

        Returns
        --------
        Model 训练好的预测模型
        MAPE: 平均绝对百分误差
        """
        # 获取模型路径
        model_path = '{0}/{1}_model/{2}.pkl'.format(self.abs_path, model_name, file_name)
        error_file_path = '{0}/json/error.json'.format(self.abs_path)

        # 如果模型不存在 获取训练数据拟合模型
        if os.path.exists(model_path) is False:
            # 训练集只是特征集的子集 所以直接取切片即可
            train_df = feature_df[start_time:'2020-07-16']

            if model_name == 'xgb':
                model = XGBRegressor(**self.xgb_best_params)
            elif model_name == 'lgb':
                model = LGBMRegressor(**self.lgb_best_params)
            else:
                print("模型不存在")
                return
            model, mape = self.fit_model(model, train_df, 0.8, model_path)

            try:
                with open(error_file_path, 'r+', encoding='utf-8') as f:
                    error_dict = json.load(f)
                    if error_dict[model_name].get(file_name, 0) == 0:
                         error_dict[model_name].update({file_name: mape})
                    else:
                        error_dict[model_name][file_name] = mape
                    f.seek(0)
                    f.truncate()
                    json.dump(error_dict, f)
            except KeyError as e:
                print(e)
                return
        else:
            # 调取训练模型
            model = joblib.load(model_path)

            try:
                with open(error_file_path, 'r', encoding='utf-8') as f:
                    error_dict = json.load(f)
                    mape = error_dict[model_name][file_name]
            except KeyError as e:
                print(e)
                return

        return model, mape

    def forecast_day_flow(self, model_name, feature_df, file_name, n_steps=168):
        """以每一天作为时间刻度进行预测 

        Parameters
        ----------
        model_name: 模型名称
        feature_df: dataframe格式的特征集
        file_name: 文件名称
        n_steps:   预测步长

        Returns
        --------
        DataFrame index = 'day' columns = ['weekday', 'month', 'y']
        MAPE: 平均绝对百分误差
        """
        start_time = '2020-03-01'
        model, mape = self.get_fitted_model(model_name, feature_df, file_name, start_time)

        # 取7月14日之后的特征集
        feature_df = feature_df['2020-07-14':]

        moving_avg = 3
        predict_list = []
        # 获取预测日期之前三天的客流量 取平均值
        for i in range(n_steps):
            index = i + moving_avg
            feature_df.MA[index] = \
                sum(feature_df.y.values[index - moving_avg:index]) / moving_avg
            df = feature_df[index:index + 1]
            X, y = df.drop(['y'], axis=1), df.y

            prediction = model.predict(X)[0]
            feature_df.y[index:index + 1] = int(prediction)
            predict_list.append(prediction)

        predict_df = feature_df.iloc[moving_avg:]
        predict_df = predict_df[['weekday', 'month', 'y']]

        return predict_df, np.array(predict_list), mape

    def forecast_hour_flow(self, model_name, feature_df, file_name, n_steps=7):
        """以每天的某小时作为时间刻度进行预测

        Parameters
        ----------
        model_name: 模型名称
        feature_df: dataframe格式的特征集
        file_name: 文件名称
        n_steps:   预测步长

        Returns
        --------
        DataFrame index = 'day' columns = ['weekday', 'month', 'y'] 
        """
        start_time = '2020-05-01'
        model, mape = self.get_fitted_model(model_name, feature_df, file_name, start_time)

        #取7月17日之后的特征集
        feature_df = feature_df['2020-07-17':]

        predict_list = []
        for i in range(n_steps):
            df = feature_df[i:i + 1]
            X, y = df.drop(['y'], axis=1), df.y
          
            prediction = model.predict(X)[0]
            feature_df.y[i:i + 1] = int(prediction)
            predict_list.append(prediction)

        predict_df = feature_df.iloc[:]
        predict_df = predict_df[['weekday', 'month', 'y']]

        return predict_df, np.array(predict_list), mape

    def forecast_by_factor(self, **params):
        """
        根据预测因子重新进行拟合
        处于速度和数据量的考量 仅更新单日预测

        返回预测结果y
        """
        date = params['date']
        weather = params['weather']
        temp = params['temp']

        feature_df = self.feature_day.copy()
    
        feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']] = \
            feature_df[['weekday', 'month', 'is_hoilday', 'y', 'mean_temp']].astype('int')
        feature_df['MA'] = feature_df['MA'].astype('float')

        feature_df.day = pd.to_datetime(feature_df.day)
        feature_df.set_index('day', inplace=True)

        feature_df.loc[date, 'weather'] = weather
        feature_df.loc[date, 'mean_temp'] = temp

        feature_df = self.feature_coding(feature_df)

        end = datetime.datetime.strptime(date, '%Y-%m-%d')
        start = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')
        steps = int((end - start) / pd.Timedelta(1, 'D'))

        predict_df = self.model_ensemble(feature_df, '%s_%s' % (weather, temp), n_steps=steps)

        return predict_df.loc[date].y

class HoltWinters(BaseModel):
    """三指数平滑模型
    """

    def __init__(self):
        super().__init__()
        self.slen = 7
        self.alpha = 0.22
        self.beta = 0.03
        self.gamma = 0.41
        self.n_preds = 30
        self.scaling_factor = 1.96

    def initial_trend(self):
        '''
        初始化趋势项
        '''
        sum = 0.0

        for i in range(self.slen):
            # 计算斜率并累加
            sum += float(self.series[i + self.slen] - self.series[i]) / self.slen

        # 返回平均值作为趋势项的初始值
        return sum / self.slen

    def initial_seasonal_components(self):
        '''
        初始化季节项
        '''
        seasonals = {}
        season_averages = []

        # 计算出周期的数目
        n_seasons = int(len(self.series) / self.slen)

        # 计算季节平均
        for j in range(n_seasons):
            season_averages.append(sum(self.series[self.slen * j:self.slen * j + self.slen]) / float(self.slen))

        # 计算初始值
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.0
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen * j + i] - season_averages[j]
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

        for i in range(len(self.series) + self.n_preds):
            if i == 0:  # 成分初始化
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(seasonals[i % self.slen])
                self.PredictedDeviation.append(0)
                self.UpperBond.append(self.result[0] + self.scaling_factor * self.PredictedDeviation[0])
                self.LowerBond.append(self.result[0] - self.scaling_factor * self.PredictedDeviation[0])
                continue

            if i >= len(self.series):  # 预测
                m = i - len(self.series) + 1
                self.result.append((smooth + m * trend) + seasonals[i % self.slen])

                # 预测时在每一步增加不确定性
                self.PredictedDeviation.append(self.PredictedDeviation[-1] * 1.01)
            else:
                val = self.series[i]
                last_smooth, smooth = smooth, self.alpha * (val - seasonals[i % self.slen]) + (1 - self.alpha) * (
                            smooth + trend)
                trend = self.beta * (smooth - last_smooth) + (1 - self.beta) * trend
                seasonals[i % self.slen] = self.gamma * (val - smooth) + (1 - self.gamma) * seasonals[i % self.slen]
                self.result.append(smooth + trend + seasonals[i % self.slen])

                # 据Brutlag算法计算偏差
                self.PredictedDeviation.append(self.gamma * np.abs(self.series[i] - self.result[i])
                                               + (1 - self.gamma) * self.PredictedDeviation[-1])

            self.UpperBond.append(self.result[-1] + self.scaling_factor * self.PredictedDeviation[-1])
            self.LowerBond.append(self.result[-1] - self.scaling_factor * self.PredictedDeviation[-1])

            self.Smooth.append(smooth)
            self.Trend.append(trend)

            self.Season.append(seasonals[i % self.slen])

    @staticmethod
    def timeseriesCVscore(params, series, loss_function=mean_squared_error, slen=7):
        errors = []
        values = series.values
        alpha, beta, gamma = params

        # 设定交叉验证折数
        tscv = TimeSeriesSplit(n_splits=3)

        for train, test in tscv.split(values):
            model = HoltWinters(series=values[train], slen=slen, alpha=alpha, beta=beta, gamma=gamma, n_preds=len(test))
            model.triple_exponential_smoothing()

            predictions = model.result[-len(test):]
            actual = values[test]

            error = loss_function(predictions, actual)
            errors.append(error)

        return np.mean(np.array(errors))

    @staticmethod
    def plotHoltWinters(series, plot_intervals=False, plot_anomalies=False):
        """
            series - 时序数据集
            plot_intervals - 显示置信区间
            plot_anomalies - 显示异常值
        """
        plt.figure(figsize=(20, 10))
        plt.plot(model.result, label="Model")
        plt.plot(series.values, label="Actual")
        error = mean_absolute_percentage_error(series.values, model.result[:len(series)])
        plt.title("Mean Absolute Percentage Error: {0:.2f}%".format(error))

        if plot_anomalies:
            anomalies = np.array([np.NaN] * len(series))
            anomalies[series.values < model.LowerBond[:len(series)]] = series.values[
                series.values < model.LowerBond[:len(series)]]
            anomalies[series.values > model.UpperBond[:len(series)]] = series.values[
                series.values > model.UpperBond[:len(series)]]

            plt.plot(anomalies, "o", markersize=10, label="Anomalies")

        if plot_intervals:
            plt.plot(model.UpperBond, "r--", alpha=0.5, label="Up/Low confidence")
            plt.plot(model.LowerBond, "r--", alpha=0.5)
            plt.fill_between(x=range(0, len(model.result)), y1=model.UpperBond, y2=model.LowerBond, alpha=0.2,
                             color="grey")

        plt.vlines(len(series), ymin=min(model.LowerBond), ymax=max(model.UpperBond), linestyles='dashed')
        plt.axvspan(len(series) - 30, len(model.result), alpha=0.3, color='lightgrey')
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc="best", fontsize=13)
        plt.savefig('./pic.png')

    def search_best_params(self, series):
        data = series[:-30]  # 留置一些数据用于测试

        # 初始化模型参数alpha、beta、gamma
        x = [0, 0, 0]

        # 最小化损失函数
        opt = minimize(HoltWinters.timeseriesCVscore, x0=x, args=(data, mean_squared_log_error), method="TNC", \
                       bounds=((0, 1), (0, 1), (0, 1)))

        # 取最优值
        alpha_final, beta_final, gamma_final = opt.x
        print(alpha_final, beta_final, gamma_final)

        return opt.x

    def predict_to_csv(self):
        self.series = self.get_day_feature_series()

        self.triple_exponential_smoothing()

        flow_list = model.result[len(model.series):]

        pred_df = pd.DataFrame(flow_list, columns=['y'])
        pred_df.y = pred_df.y.astype('int')

        date_list = pd.date_range(start='20200717', freq='D', periods=30)

        pred_df['day'] = date_list
        pred_df['weekday'] = pred_df.day.dt.weekday + 1
        pred_df['month'] = pred_df.day.dt.month

        pred_df.to_csv('./pred_holtwinters_day.csv', encoding='gb18030', index=0)

class ArimaModel(BaseModel):
    """SARIMA模型
        仅用于预测一个月的客流
    """

    def __init__(self):
        super().__init__()

        self.param = {'p': 2, 'd': 1, 'q': 2, 'P': 0, 'Q': 1, 'D': 1, 's': 7}

    def tsplot(self, y, lags=None, figsize=(12, 7), style='bmh'):
        """
            绘制时序及其ACF（自相关性函数）、PACF（偏自相关性函数），计算迪基-福勒检验
            y - 时序
            lags - ACF、PACF计算所用的时差
        """
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        with plt.style.context(style):
            fig = plt.figure(figsize=figsize)
            layout = (2, 2)
            ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
            acf_ax = plt.subplot2grid(layout, (1, 0))
            pacf_ax = plt.subplot2grid(layout, (1, 1))

            y.plot(ax=ts_ax)
            p_value = sm.tsa.stattools.adfuller(y)[1]
            ts_ax.set_title('Time Series Analysis Plots\n Dickey-Fuller: p={0:.5f}'.format(p_value))
            smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
            smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
            plt.tight_layout()

    def optimizeSARIMA(self, parameters_list, d, D, s):
        """
        返回参数和相应的AIC的dataframe
            parameters_list - (p, q, P, Q)元组列表
            d - ARIMA模型的单整阶
            D - 季节性单整阶
            s - 季节长度
        """
        results = []
        best_aic = float("inf")

        for param in tqdm_notebook(parameters_list):

            # 由于有些组合不能收敛，所以需要使用try-except

            try:
                model = sm.tsa.statespace.SARIMAX(series, order=(param[0], d, param[1]),

                                                  seasonal_order=(param[3], D, param[3], s)).fit(disp=-1)
            except:
                continue

            aic = model.aic

            # 保存最佳模型、AIC、参数
            if aic < best_aic:
                best_model = model
                best_aic = aic
                best_param = param

            results.append([param, model.aic])

        result_table = pd.DataFrame(results)
        result_table.columns = ['parameters', 'aic']

        # 递增排序，AIC越低越好
        result_table = result_table.sort_values(by='aic', ascending=True).reset_index(drop=True)

        return result_table

    def plotSARIMA(self, series, model, n_steps):
        """
            绘制模型预测值与实际数据对比图
            series - 时序数据集
            xgb_model - SARIMA模型
            n_steps - 预测未来的步数
        """
        data = pd.DataFrame(series.values, columns=['actual'], index=series.index)
        data['arima_model'] = model.fittedvalues.values

        # 平移s+d步，因为差分的缘故，前面的一些数据没有被模型观测到
        data['arima_model'][:s + d] = np.NaN

        forecast = model.predict(start=data.shape[0], end=data.shape[0] + n_steps)
        forecast = data.arima_model.append(forecast)

        # 计算误差，同样平移s+d步
        error = mean_absolute_percentage_error(data['actual'][s + d:], data['arima_model'][s + d:])

        plt.figure(figsize=(15, 7))
        plt.title("Mean Absolute Percentage Error: {0:.2f}%".format(error))
        plt.plot(forecast, color='r', label="xgb_model")
        plt.axvspan(data.index[-1], forecast.index[-1], alpha=0.5, color='lightgrey')
        plt.plot(data.actual, label="actual")
        plt.legend()
        plt.grid(True)
        plt.savefig('./arima.png')

    def forecast_day_flow(self, n_steps=30):
        """获取每日客流特征集
        Parameters
        ----------
        n_steps: 预测步长 默认为30 即预测最近30天的客流
        Returns
        -------
        Series: 特征集
        """
        series = self.get_day_feature_series()

        pdq = self.param['p'], self.param['d'], self.param['q']
        PDQS = self.param['P'], self.param['D'], self.param['Q'], self.param['s']

        best_model = sm.tsa.statespace.SARIMAX(series, order=pdq, seasonal_order=PDQS).fit(disp=-1)

        data = pd.DataFrame(series.values, columns=['actual'], index=series.index)

        data['arima_model'] = best_model.fittedvalues.values

        offest = self.param['s'] + self.param['d']
        # 平移s+d步，因为差分的缘故，前面的一些数据没有被模型观测到
        data['arima_model'][:offest] = np.NaN

        forecast = best_model.predict(start=data.shape[0], end=data.shape[0] + n_steps - 1)

        # 计算误差，同样平移s+d步
        error = mean_absolute_percentage_error(data['actual'][offest:], data['arima_model'][offest:])
        print('mape error: ', error)

        return forecast

    def predict_to_csv(self):
        """将模型输出保存为csv格式
        """
        pred_series = self.forecast_day_flow(30)

        pred_df = pd.DataFrame(pred_series.values, index=pred_series.index, columns=['y'])

        pred_df.y = pred_df.y.astype('int')
        pred_df.reset_index(inplace=True)

        pred_df.columns = ['day', 'y']
        pred_df['weekday'] = pred_df.day.dt.weekday + 1
        pred_df['month'] = pred_df.day.dt.month

        pred_df.to_csv('./pred_arima_day.csv', encoding='gb18030', index=0)

        return pred_df

if __name__ == '__main__':
    ml = MLPredictor()
    feature_df = ml.get_day_feature()
    print(feature_df)
    df = ml.model_ensemble(feature_df, 'day')
    print(df)
    # ml.forecast_by_factor('2020-07-17', choose_wea = '阴', choose_temp = '22')
    # j = 0

    # for i in range(6, 22):
    #     k = 0
    #     for sta in SQLOS.get_station_dict().keys():

    #         feature_df = bp.get_sta_hour_feature(sta, str(i), 'out')

    #         df = bp.forecast_hour_flow(feature_df, 'out_hour/%s_%d'%(sta, i))
    #         df.reset_index(level='time', inplace=True)
    #         df['sta'] = sta
    #         if k == 0:
    #             ddf = df
    #         else:
    #             ddf = ddf.append(df)

    #         k += 1
    #         print(k)
    #     if j == 0:
    #         dddf = ddf
    #     else:
    #         dddf = dddf.append(ddf)
    #     j += 1
    #     print(j)

    # dddf.to_csv('./test.csv', encoding = 'gb18030', index = 0)


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
    # xgb_model = HoltWinters(series, 7, 0.22334736563502622, 0.03323882022600311, 0.4090198141980643, 90)
    # xgb_model.triple_exponential_smoothing()
    # plotHoltWinters(series)
