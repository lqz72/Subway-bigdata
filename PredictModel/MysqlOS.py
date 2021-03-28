# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import MySQLdb
import configparser
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
        abs_path = os.path.abspath(os.path.dirname(__file__))

        cf= configparser.ConfigParser()
        cf.read(abs_path + '/mysql.conf', encoding='utf-8')

        #远程数据库连接
        # conn = MySQLdb.connect(host='118.178.88.14', port=3306, user='lqz',
        # passwd='863JTcyPGezGEXmm', db='lqz', charset='utf8mb4')

        #本地数据库连接
        conn = MySQLdb.connect(
            host=cf.get('Default', 'DB_HOST'),
            port=cf.getint('Default', 'DB_PORT'),
            user=cf.get('Default', 'DB_USER'),
            passwd=cf.get('Default', 'DB_PASSWD'),
            db=cf.get('Default', 'DB_NAME'),
            charset='utf8mb4',
        )
   
        return conn
    
    def load_data():
        '''
        将本地txt文件上传到mysql
        '''
        db = SQLOS.connect_to_db()
        cursor = db.cursor()

        abs_path = 'd:/Python/code/Subway-bigdata/PredictModel/txt_data/'
        file_path = {
            # 'feature2020':  abs_path + 'feature2020.txt',
            # 'weather2020': abs_path + 'weather2020.txt',
            # 'hoilday2020': abs_path + 'hoilday2020.txt',
            # 'station': abs_path + 'station.txt',
            # 'users': abs_path + 'users.txt',
            # 'flow': abs_path + 'flow.txt',
            # 'trips': abs_path +'trips.txt', 
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
            print('success load all data to mysql!')

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

    def get_station_dict():
        '''
        返回有序站点字典 
        '''
        sta_df = SQLOS.get_df_data('station')[['sta_name', 'line']]
        sta_df = sta_df.sort_values(by='sta_name', key=lambda x:
            x.str.lstrip('Sta').astype('int'))

        sta_dict = dict(zip(sta_df['sta_name'], sta_df['line']))

        return sta_dict

    def get_clean_data():
        '''
        数据清洗 并将合法数据存入mysql
        '''
        #删去空缺值和重复行
        trips_df = SQLOS.get_df_data('trips')
        trips_df.dropna(axis = 0, how = 'any', inplace = True)
        trips_df.drop_duplicates(inplace=True)
        
    
        in_df = trips_df.loc[:,['user_id', 'in_sta_name','in_time']]
        out_df = trips_df.loc[:,['user_id', 'out_sta_name','out_time']]

        #获取站点列表
        sta_list = SQLOS.get_station_dict().keys()

        # 获取所有进站行程中出现的站点
        in_sta_list = trips_df['in_sta_name'].tolist()
        out_sta_list = trips_df['out_sta_name'].tolist()
        trips_sta_set = set(in_sta_list + out_sta_list)

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
        获取原始客流信息 每一条为单个用户进出站的记录 返回一个dataframe
        '''
        trips_df = SQLOS.get_df_data('trips')
        trips_df.drop(['price', 'id'], axis=1, inplace=True)

        trips_df['in_time'] = pd.to_datetime(trips_df['in_time'])
        trips_df['out_time'] = pd.to_datetime(trips_df['out_time'])

        return trips_df

    def get_in_out_df():
        '''
        返回入/出站记录dataframe
        '''
        in_df = SQLOS.get_df_data('in_trips')
        out_df = SQLOS.get_df_data('out_trips')

        in_df.in_time = pd.to_datetime(in_df.in_time)
        in_df.set_index('in_time', inplace =True)
        out_df.out_time = pd.to_datetime(out_df.out_time)
        out_df.set_index('out_time', inplace =True)
  
        in_df.drop(['id', 'user_id'], axis=1, inplace=True)
        out_df.drop(['id', 'user_id'], axis=1, inplace=True)
        
        return in_df, out_df

    def get_user_df():
        '''
        返回所有用户信息dataframe
        '''
        user_df = SQLOS.get_df_data('users')
        user_df.drop('id', axis=1, inplace=True)

        return user_df

    def get_admin_info():
        '''
        返回管理员账号信息 返回一个列表
        '''
        df = SQLOS.get_df_data('admin')

        admin_list = []
        for i in range(df.shape[0]):
            name = df['name'].values[i]
            pwd = df['pwd'].values[i]
            tips = df['tips'].values[i]
            admin_dict = {'name': name, 'pwd': pwd, 'tips': tips}
            admin_list.append(admin_dict)

        return admin_list

    def get_weather_info(date):
        '''
        获取当日天气信息
        '''
        conn = SQLOS.connect_to_db()

        try:
            sql = 'SELECT weather from weather2020 WHERE `day` = "%s"' %  date
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            return data

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()
        
        return 'UnKnow'
        
    def get_hoilday_info(date):
        '''
        获取当日节假日信息
        '''
        conn = SQLOS.connect_to_db()

        try:
            sql = 'SELECT is_hoilday from hoilday2020 WHERE `day` = "%s"' %  date
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            return data

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()
        
        return 'UnKnow'

