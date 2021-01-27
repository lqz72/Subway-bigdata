from DataSource import *

def get_weekday_flow():
    '''
    获取不同月份每周客流量 
    返回一个字典 格式{'month':{'weekday':num}}
    '''
    flow_df = DataSource().get_flow_df()
    week_flow = flow_df.groupby(by = ['month', 'weekday'])['站点'].count()
    week_flow.sort_index()
    month_list = [i for i in range(13)]
    month_list.remove(0)

    exist_month_list = list(set([i[0] for i in week_flow.index]))
    week_flow_dict = {}
    for i in exist_month_list:
        temp_dict = {j: week_flow[i][j] for j in [k for k in week_flow[i].index]}
        week_flow_dict[i] = temp_dict

    return week_flow_dict
