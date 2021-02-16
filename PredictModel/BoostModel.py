import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder   
from xgboost import XGBRegressor, XGBClassifier
import joblib
import os
from sys import path
#测试使用
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei为黑体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

scaler = StandardScaler() #标准化缩放器

tscv = TimeSeriesSplit(n_splits=5)  #五折交叉验证

abs_path = os.path.abspath(os.path.dirname(__file__)) + '/csv_data/'
file_path = {
    'flow': abs_path + 'flow.csv',
    'hoilday': abs_path + 'hoilday2020.csv',
    'weather': abs_path + 'weather2020.csv'
}

def mean_absolute_percentage_error(y_true, y_pred):
    '''
    自定义平均绝对百分误差
    '''
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def get_train_data():
    '''
    获取训练数据
    '''
    flow_df = pd.read_csv(file_path['flow'], encoding='gb18030')
    hoilday_df = pd.read_csv(file_path['hoilday'], encoding='gb18030', names = ['day', 'is_hoilday'])
    weather_df = pd.read_csv(file_path['weather'], encoding='gb18030')
    
    flow_df['y'] = 1
    flow_df = flow_df.groupby(by = ['day', 'weekday', 'month'], as_index = False)['y'].count()
    #flow_df['is_weekend'] = flow_df.weekday.isin([6,7])*1
    flow_df['day'] = flow_df['day'].apply(pd.to_datetime)
    flow_df = flow_df[flow_df['day'] >= '2020-01-01']
    flow_df.index = range(flow_df.shape[0])
    
    weather_df.drop('day', axis=1, inplace=True)
    train_df = pd.concat([flow_df, hoilday_df.is_hoilday, weather_df], axis=1)
    train_df.dropna(inplace=True)
    train_df[['weekday', 'month', 'y']] = train_df[['weekday', 'month', 'y']].astype('int')

    #滑窗 window = 5 MA1~MA7相关性系数过高 只采取一种
    train_df['MA5'] = train_df['y'].rolling(5).mean()

    #去掉最高和最低 保留二者平均
    train_df.drop(['high_temp', 'low_temp'], axis = 1, inplace = True)
    train_df.dropna(inplace=True)
    
    return train_df

def feature_coding(train_df):
    '''
    对特征进行编码
    '''
    #气温信息对于数值敏感 采用label编码
    train_df.mean_temp = LabelEncoder().fit_transform(train_df.mean_temp)

    #天气状况与数值无关 采用one-hot编码
    train_df = pd.get_dummies(train_df)

    return train_df

def train_test_split(X, y, train_size=0.9):
    '''
    划分训练集和测试集
    '''
    X_length = X.shape[0]
    split = int(X_length*train_size)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test

def plotModelResults(model, X_train, X_test, y_train, y_test, plot_intervals=False, plot_anomalies=False):  
    '''
    预测可视化
    '''
    prediction = model.predict(X_test)

    plt.figure(figsize=(15, 7))
    
    plt.plot(prediction, "g", label="prediction", linewidth=2.0)
    plt.plot(y_test.values, label="actual", linewidth=2.0)

    if plot_intervals:
        cv = cross_val_score(model, X_train, y_train, cv=tscv, scoring="neg_mean_absolute_error")
        
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

    return error

def short_forecast(train_df, train_size):
    '''
    短期时序预测 
    '''
    train_df.set_index('day', inplace=True)
    
    X, y  = train_df.drop('y', axis = 1), train_df.y
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size)

    #标准化处理
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    #回归器
    reg = XGBRegressor()
    reg.fit(X_train, y_train)
 
    error = plotModelResults(reg, X_train=X_train, X_test=X_test, y_train=y_train
        , y_test=y_test, plot_intervals=True)
    
    joblib.dump(reg, 'test_model.pkl') 
    print(error)
   
def get_best_param(X_train, y_train):
    '''
    调参
    '''
    pass

df = feature_coding(get_train_data())
short_forecast(df, 0.9)


