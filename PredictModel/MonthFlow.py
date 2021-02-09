from DataSource import *
from pyecharts import options as opts
from pyecharts.charts import Line, Timeline

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

def month_line(month_dict) -> Line:
    '''
    绘制单月整体客流分布
    返回一个Line图表
    '''
    tl = Timeline()
    for i in month_dict:
        day = month_dict[i].keys()
        flow = [str(j) for j in month_dict[i].values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "{}月客流".format(int(i[-2:])),
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="单月整体客流波动"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "日期", type_="category", boundary_gap=False),
            )
        )
        tl.add(line, "{0}年{1}月".format(i[0:4], int(i[-2:])))
    return tl
    
month_dict = get_month_flow()
# month_line(month_dict)