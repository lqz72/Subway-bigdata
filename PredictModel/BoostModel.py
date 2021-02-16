import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error
from scipy.optimize import minimize
from xgboost import XGBRegressor 
from sys import path
import os

def mean_absolute_percentage_error(y_true, y_pred):
    '''
    自定义平均绝对百分误差
    '''
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


abs_path = os.path.abspath(os.path.dirname(__file__)) + '/csv_data/'
file_path = {
    'flow': abs_path + 'flow.csv',
    'hoilday': abs_path + 'hoilday.csv',
    'weather': abs_path + 'weather.csv'
}

def get_train_data():
    '''
    获取训练数据
    '''
    flow_df = pd.read_csv(file_path['flow'], encoding='gb18030')
    hoilday_df = pd.read_csv(file_path['hoilday'], encoding='gb18030', names = ['day', 'is_hoilday'])
    weather_df = pd.read_csv(file_path['weather'], encoding='gb18030' )

    hoilday_df.day = pd.to_datetime(hoilday_df.day)
    weather_df.day = pd.to_datetime(weather_df.day)
    weather_df.drop('day', axis=1, inplace=True)
    
    flow_df['y'] = 1
    flow_df = flow_df.groupby(by = ['day', 'weekday', 'month'], as_index = False)['y'].count()
    #flow_df['is_weekend'] = flow_df.weekday.isin([6,7])*1
    flow_df['day'] = flow_df['day'].apply(pd.to_datetime)
    flow_df = flow_df[flow_df['day'] >= '2020-01-01']
    flow_df.index = range(flow_df.shape[0])

    train_df = pd.concat([flow_df, hoilday_df.is_hoilday, weather_df], axis = 1)
    train_df.dropna(inplace=True)
    
    return train_df

def get_sta_df(df, sta_name):
    return df[df['sta'] == sta_name]

def train_test_split(X, y, train_size=0.9):
    '''
    划分训练集和测试集
    '''
    X_length = X.shape[0]
    split = int(X_length*train_size)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test

df = get_train_data()
print(df)
