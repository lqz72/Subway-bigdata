from DataSource import *

def get_sta_flow():
    '''
    单站的点出/入站客流分析
    返回两个字典 分别存储进站和出站数据 格式{'station_name':num}
    '''
    in_df, out_df = DataSource().clean_data()
    
    #转换为标准时间格式
    in_df.loc[:,"进站时间"] = pd.to_datetime(in_df["进站时间"])
    out_df.loc[:,"出站时间"] = pd.to_datetime(out_df["出站时间"])

    #重组聚合
    in_data_dict = {}
    grouped = in_df.groupby(by="进站名称")
    for station, df_time in grouped:
        df_time.set_index("进站时间", inplace =True)
        #时间序列重采样
        rs = df_time.resample("M").count()["进站名称"]
        in_time = [x.strftime('%Y-%m-%d') for x in rs.index]
        in_amount = rs.values
        in_data_dict[station] = dict(zip(in_time, in_amount))

    out_data_dict = {}
    grouped = out_df.groupby(by="出站名称")

    for station, df_time in grouped:
        df_time.set_index("出站时间", inplace =True)
        rs = df_time.resample("M").count()["出站名称"]
        out_time = [x.strftime('%Y-%m-%d') for x in rs.index]
        out_amount = rs.values
        out_data_dict[station] = dict(zip(out_time, out_amount))

    return in_data_dict, out_data_dict

print(get_sta_flow())
