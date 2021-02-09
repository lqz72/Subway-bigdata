from DataSource import *
from pyecharts import options as opts
from pyecharts.charts import Bar


def get_sta_flow():
    '''
    单站的点出/入站客流分析
    返回两个字典 分别存储进站和出站数据 格式{'station_name':{'month':num}}
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
        in_time = [x.strftime('%Y-%m') for x in rs.index]
        in_amount = rs.values
        in_data_dict[station] = dict(zip(in_time, in_amount))

    out_data_dict = {}
    grouped = out_df.groupby(by="出站名称")

    for station, df_time in grouped:
        df_time.set_index("出站时间", inplace =True)
        rs = df_time.resample("M").count()["出站名称"]
        out_time = [x.strftime('%Y-%m') for x in rs.index]
        out_amount = rs.values
        out_data_dict[station] = dict(zip(out_time, out_amount))

    return in_data_dict, out_data_dict

def station_bar(station, in_dict, out_dict):
    in_dict, out_dict = in_dict[station], out_dict[station]
    month_list = list(in_dict.keys())
    in_flow = [str(i) for i in in_dict.values()]
    out_flow = [str(i) for i in out_dict.values()]

    colors = ["#5793f3", "#d14a61"]
    bar = (
        Bar()
        .add_xaxis(xaxis_data=month_list)
        .add_yaxis(
            series_name="入站",
            y_axis=in_flow,
            yaxis_index=0,
            color=colors[1],
            label_opts=opts.LabelOpts(is_show=False)
        )
        .add_yaxis(
            series_name="出站",
            y_axis=out_flow,
            yaxis_index=1,
            color=colors[0],
            label_opts=opts.LabelOpts(is_show=False)
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="出站客流",
                type_="value",
                position="right",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color=colors[1])
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            )
        )

        .set_global_opts(
            title_opts=opts.TitleOpts(title="{}号站点入/点出客流统计".format(int(station[3:]))),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                name="入站客流量",
                type_="value",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color=colors[0])
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
        )
        # .render("station_flow.html")
    )
    return bar

in_dict, out_dict = get_sta_flow()
#station_bar('Sta1', in_dict, out_dict)