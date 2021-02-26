# -*- coding: utf-8 -*-
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import MySQLdb
import os
import time

class SQLOS(object):
    '''
    数据库交互 提供数据读写接口

    注意事项：
        由于数据量的限制 使用pymysql对百万级别的数据进行读写速度很慢
        因此数据库的读取采取MySQLdb进行连接 pandas.read_sql转化为dataframe
        将dataframe导入数据库需要使用pandas.io.sql.to_sql 所以需要采取sqlalchemy引擎
    '''
    def __init__(self):
        pass
    
    def connect_to_db():
        #远程数据库连接
        # conn = MySQLdb.connect(host='118.178.88.14', port=3306, user='lqz',
        # passwd='863JTcyPGezGEXmm', db='lqz', charset='utf8mb4')

        #本地数据库连接
        conn = MySQLdb.connect(host='localhost', port=3306, user='root',
        passwd='yongfufan', db='data', charset='utf8mb4')
   
        return conn
    
    def load_data():
        '''
        将本地txt文件上传到mysql
        '''
        db = SQLOS.connect_to_db()
        cursor = db.cursor()

        abs_path = 'd:/Python/code/Subway-bigdata/PredictModel/txt_data/'
        file_path = {
            'feature2020':  abs_path + 'feature2020.txt',
            'weather2020': abs_path + 'weather2020.txt',
            'hoilday2020': abs_path + 'hoilday2020.txt',
            'station': abs_path + 'station.txt',
            'users': abs_path + 'users.txt',
            'flow': abs_path + 'flow.txt',
            'trips': abs_path +'trips.txt', 
        }

        try:
            for name, path in file_path.items():
                print('正在载入%s中的数据' % name)
                start = time.time()

                sql = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES"  % (path, name)
                cursor.execute(sql)
                db.commit()

                end = time.time()
                print('读取时间:', end - start)

            db.close()
            print('seccess load all data to mysql!')

        except Exception as e:
            print('error:', e)
            db.rollback()
            db.close() 

    def get_df_data(table_name):
        '''
        从数据库中读取对应数据表的数据并以dataframe的方式返回
        '''
        conn = SQLOS.connect_to_db()

        if table_name in ['feature', 'hoilday', 'weather']:
            table_name += '2020'

        try:
            print('正在读取%s中的数据' % table_name)
            start = time.time()

            sql = 'SELECT * FROM %s' % table_name
            df = pd.read_sql(sql, con=conn)
            
            end = time.time()
            print('读取时间:', end - start)
            conn.close()
            return df
        except Exception as e:
            conn.rollback()
            conn.close()
            print('error', e)

    def write_df_data(df, table_name):

        '''
        将dataframe写入mysql对应的表中
        '''
        conn = create_engine('mysql+pymysql://root:yongfufan@localhost:3306/data?charset=utf8mb4')

        pd.io.sql.to_sql(df, table_name, con=conn, if_exists='replace', index=None)

        print('success write dataframe to mysql!')
    
    def get_age_data():
        '''
        获取年龄分布 返回一个字典 {'age': amount,}
        '''
        user_df = SQLOS.get_df_data('users')
    
        user_df.birth_year = user_df.birth_year.apply(lambda x: -int(x) + 2021)

        age_series = user_df.groupby(by="birth_year").count()["user_id"]
        age_index = age_series.index
        age_values = age_series.values

        # 创建一个字典用于存放 各年龄所对应的用户人数
        age_dict = dict(zip(age_index, age_values))
        #print(age_dict)
        return age_dict

    def get_station_list():
        '''
        返回有序站点列表
        '''
        sta_list = SQLOS.get_df_data('station')['sta_name'].tolist()
        sta_list.sort(key=lambda x: int(x[3:]))
        return sta_list

    def get_clean_data():
        '''
        数据清洗 并将进站和出站信息存入mysql
        '''
        #删去空缺值和重复行
        trips_df = SQLOS.get_df_data('trips')
        trips_df.dropna(axis = 0, how = 'any', inplace = True)
        trips_df.drop_duplicates(inplace=True)
        
    
        in_df = trips_df.loc[:,['user_id', 'in_sta_name','in_time']]
        out_df = trips_df.loc[:,['user_id', 'out_sta_name','out_time']]

        #获取站点列表
        sta_list = SQLOS.get_station_list()

        # 获取所有进站行程中出现的站点
        in_sta_list = trips_df['in_sta_name'].tolist()
        out_sta_list = trips_df['out_sta_name'].tolist()
        trips_sta_set = set(in_sta_list + out_sta_list)

        # 非法的站点名称 ['Sta104', 'Sta14', 'Sta5', 'Sta155', 'Sta98']
        ill_sta_list = list((set(sta_list) ^ trips_sta_set))

        #经验证 trips.csv中存在不存在的站点以及错误的站点名  需要删去 32583条
        index_list_in = trips_df[trips_df['in_sta_name'].isin(ill_sta_list)].index.tolist()
        in_df.drop(index_list_in, axis = 0, inplace = True)

        index_list_out = trips_df[trips_df['out_sta_name'].isin(ill_sta_list)].index.tolist()
        out_df.drop(index_list_out, axis=0, inplace=True)


        SQLOS.write_df_data(in_df, 'in_trips')
        SQLOS.write_df_data(out_df, 'out_trips')

    def get_flow_df():
        '''
        获取所有客流信息 即每一条进出站记录 返回一个dataframe
        dataframe格式如下  
              sta             time         day      weekday month
        0   Sta51  2019/12/26 10:07  2019-12-26         4     12
        1   Sta63  2019/12/26 10:37  2019-12-26         4     12
        2   Sta129 2019/12/26 10:42  2019-12-26         4     12
        3   Sta25  2019/12/26 11:34  2019-12-26         4     12
        4   Sta78  2019/12/26 13:10  2019-12-26         4     12

        [1517815 rows x 5 columns]
        '''
        flow_df = SQLOS.get_df_data('flow')
        flow_df.drop('id', axis=1, inplace=True)
        flow_df.day = pd.to_datetime(flow_df.day)
    
        return flow_df
    
    def get_trips_df():
        '''
        返回入/出站记录dataframe
        '''
        in_df = SQLOS.get_df_data('in_trips')
        out_df = SQLOS.get_df_data('out_trips')

        in_df.in_time = pd.to_datetime(in_df.in_time)
        out_df.out_time = pd.to_datetime(out_df.out_time)
        
        in_df.drop(['id', 'user_id'], axis=1, inplace=True)
        out_df.drop(['id', 'user_id'], axis=1, inplace=True)
        
        return in_df, out_df

    def get_user_flow(user_id):
        '''
        获取单个用户出行记录
        返回一个列表 格式[('in_sta_name', 'in_time', 'out_sta_name', 'out_time'),]
        '''
        df = SQLOS.get_df_data('trips')
        df = df[df['user_id'] == user_id]
        grouped = df.groupby(['in_sta_name', 'in_time', 'out_sta_name', 'out_time'],
            as_index=False)['in_time']

        trip_record = []
        for record in grouped:
            trip_record.append(record[0])

        return trip_record

