from DataSource import *

def get_week_flow():
    '''
    获取不同月份每周客流量 
    返回一个字典 格式{'month':{'dayofweek':num,},}
    '''
    flow_df = DataSource().get_flow_df()
    flow_df['flow'] = 1 

    #获取所有行程中出现的年月
    month_list = DataSource.get_month_list(flow_df['day'])
    
    week_flow = flow_df.groupby(by=['day', 'dayofweek'], as_index = False)['flow'].count()
    week_flow.set_index('day', inplace=True)
    
    week_dict = {}
    for i in month_list:
        temp_df = week_flow[i]
        temp_df = temp_df.groupby(by=['dayofweek'])['flow'].sum()
        week_dict[i] = dict(zip(temp_df.index, temp_df.values))     
   
    return week_dict
    
print(get_week_flow())