from DataSource import *
from pyecharts import options as opts
from pyecharts.charts import Line, Timeline

def get_week_flow():
    '''
    获取不同月份每周客流量 
    返回一个字典 格式{'month':{'weekday':num,},}
    '''
    flow_df = DataSource().get_flow_df()
    flow_df['flow'] = 1 

    #获取所有行程中出现的年月
    month_list = DataSource.get_month_list(flow_df['day'])
    
    flow_df.set_index('day', inplace=True)

    week_dict = {}
    for i in month_list:
        temp_df = flow_df.loc[i,:]
        temp_dict = {}
        for weekday, flow in temp_df.groupby(by=['weekday']):
            grouped = flow.groupby(by = ['day'])['flow'].count()
            mean_flow = grouped.sum() / grouped.shape[0]
            temp_dict[weekday] = int(mean_flow)
        week_dict[i] = temp_dict
   
    return week_dict
    
def week_line(week_dict) -> Line:
    '''
    绘制各月工作日和周末的平均客流分布
    返回一个Line图表
    '''
    tl = Timeline()
    for i in week_dict:
        weekday = week_dict[i].keys()
        flow = [str(j) for j in week_dict[i].values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = weekday)
            .add_yaxis(
                series_name= "{}月各星期品平均客流分布".format(int(i[-2:])),
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="工作日和周末客流分析"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/平均人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "星期", type_="category", boundary_gap=False),
            )
        )
        tl.add(line, "{0}年{1}月".format(i[0:4], int(i[-2:])))
    return tl

week_dict = get_week_flow()
# week_line(week_dict)