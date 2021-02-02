from DataSource import *

def get_month_flow():
    '''
    单月整体的客流波动分析
    返回一个字典 包含每个月份客流量的数据 格式 {'year-month':{'month':flow,},}
    '''
    flow_data = DataSource().get_flow_data()
    date_flow = DataSource.get_date_series(flow_data)

    #获取所有行程中出现的年月
    month_list = DataSource.get_month_list(date_flow.index)
    
    month_dict = day_dict = {}
    for i in month_list:
        temp_series = date_flow[i]
        day = [j.strftime("%d") for j in temp_series.index]
        flow = temp_series.values
        month_dict[i] = dict(zip(day, flow))

    return month_dict

# get_month_flow()