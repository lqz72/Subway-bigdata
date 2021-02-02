from DataSource import *


def get_month_flow():
    '''
    单月整体的客流波动分析
    返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'month':flow,},}
    '''
    flow_data = DataSource().get_flow_data()
    date_flow = DataSource.get_date_series(flow_data)
