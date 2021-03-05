# -*- coding: utf-8 -*-
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.charts import Pie
from pyecharts.charts import Line, Timeline
from pyecharts.charts import Bar

class ChartApi(object):
    '''
    数据分析图表接口
    '''
    def __init__(self):
        pass

    def age_radar(age, percent) -> Radar:
        '''
        绘制年龄结构分布图
        返回一个雷达图
        '''
        c = (
            Radar()
            .add_schema(
                schema=[opts.RadarIndicatorItem(name=i, max_=60) for i in age]
            )
            .add("用户年龄分布", percent)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Radar"),
            )
        )
        return c

    def age_pie(age, percent) -> Pie:
        '''
        绘制年龄结构分布图
        返回一个饼状图
        '''
        c = (
            Pie()
            .add(
                "",
                [list(i) for i in zip(age, percent)],
                center=["40%", "50%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="用户年龄结构分布"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}%"))

        )
        return c

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

    def curr_week_line(curr_week_dict) -> Line:
        '''
        绘制本周客流波动 返回一个Line图表
        '''
        day = ['周一', '周二', '周三', '周四', '周五', '周六', '周末']
        flow = [str(j) for j in curr_week_dict.values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "客流",
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="本周客流波动"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "星期", type_="category", boundary_gap=False),
            )
        )

        return line

    def day_line(month, day_dict) -> Line:
        day = day_dict.keys()
        flow = [str(j) for j in day_dict.values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "{}月客流".format(int(month[-2:])),
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="当月客流波动"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "日期", type_="category", boundary_gap=False),
            )
        )
        return line

    def station_bar(station, in_dict, out_dict) ->Bar:
        '''
        绘制某站点出入客流分布
        返回一个Bar图表
        '''
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

    
        