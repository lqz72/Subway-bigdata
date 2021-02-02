from DataSource import *

def get_month_flow():
    '''
    单月整体的客流波动分析
    返回一个列表 包含每个月份客流量的数据 格式 [(['day',],[num,]),]
    '''
    flow_data = DataSource().get_flow_data()
    date_flow = DataSource().get_date_flow(flow_data)

    time_list = [i.strftime("%Y-%m") for i in date_flow.index]
    time_list = list(set(time_list))
    time_list.sort(key=lambda x: (int(x[2:4]), int(x[5:7])))

    month = []
    #获取每个月份 每一天所对应的总体客流量 series类型
    for i in range(len(time_list)):
        month.append(date_flow[time_list[i]])

    month_flow = []
    for i in range(8):
        time = [i.strftime("%Y-%m-%d") for i in month[i].index]
        temp = time, month[i].tolist()
        month_flow.append(temp)
    return month_flow


print(get_month_flow())
