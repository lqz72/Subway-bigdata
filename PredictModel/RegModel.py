import pandas as pd
import numpy as np
import os

'''
预测模型 方法待定 
'''
abs_path = os.path.abspath(os.path.dirname(__file__)) + '/csv_data/'
file_path = {
    'flow': abs_path + 'flow.csv',
    'hoilday': abs_path + 'hoilday.csv'
}

def get_train_data():
    '''
    获取训练数据
    '''
    flow_df = pd.read_csv(file_path['flow'], encoding='gb18030')
    hoilday_df = pd.read_csv(file_path['hoilday'], encoding='gb18030', names = ['day', 'is_hoilday'])

    flow_df['flow'] =  1
    flow_df = flow_df.groupby(by=['day', 'sta', 'dayofweek', 'month'], as_index=False)['flow'].count()
    
     #增添一列 显示星期 
    week_day = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六' , '星期日']
    flow_df['weekday'] = flow_df['dayofweek'].apply(lambda x: week_day[x - 1])

    #增添一列 表示是否为节假日(包括周末)
    #设置index
    date_index = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
    hoilday_df.index = date_index

    #获取节假日列表
    hoilday_list = hoilday_df[hoilday_df['is_hoilday'].values == 1].index
    hoilday_list = [i.strftime('%Y-%m-%d') for i in hoilday_list]
    hoilday_list.extend(['2019-12-28', '2019-12-29'])

    flow_df['day'] =  pd.to_datetime(flow_df['day'])
    def is_hoilday(x):
        if x.strftime('%Y-%m-%d') in hoilday_list:
            return True
    
    flow_df['is_hoilday'] = flow_df['day'].apply(lambda x: 1 if is_hoilday(x) == True else 0)

    #增加一列 值为前一天的客流量
    flow_df['pre_date_flow'] = flow_df.loc[:, 'flow'].shift(1)
    
    flow_df.dropna(inplace = True)

    return flow_df

def get_sta_df(df, sta_name):
    return df[df['sta'] == sta_name]

def train_test_split(X, y, train_size=0.9)
    '''
    划分训练集和测试集
    '''
    X_length = X.shape[0]
    split = int(X_length*train_size)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, X_test, y_train, y_test

df = get_train_data()
