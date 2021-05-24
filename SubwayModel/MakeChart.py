# -*- coding: utf-8 -*-
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.charts import Pie
from pyecharts.charts import Line, Timeline
from pyecharts.charts import Bar
from pyecharts.charts import Grid
from DataAnalysis import DataApi
from PredictResult import PredictApi

class ChartApi(object):
    '''
    数据分析图表接口
    '''
    def __init__(self):
        pass

    def age_bar(age, percent) -> Bar:
        '''
        绘制年龄结构分布图
        返回一个柱形图
        '''
        bar = (
            Bar()
            .add_xaxis(xaxis_data=age)
            .add_yaxis(
                series_name="",
                y_axis=percent,
                yaxis_index=0,
                label_opts=opts.LabelOpts(is_show=False)
            )

            .set_global_opts(
                title_opts=opts.TitleOpts(title="用户年龄结构柱状图", pos_left="center"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="百分比%",
                    type_="value",
                    axislabel_opts=opts.LabelOpts(formatter="{value}"),
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                ),
            )
            # .renderer('./test.html')
        )
        grid = Grid()
        grid.add(chart=bar, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

    def age_pie(age, percent) -> Pie:
        '''
        绘制年龄结构分布图
        返回一个饼状图
        '''
        pie = (
            Pie()
            .add(
                "",
                [list(i) for i in zip(age, percent)],
                center=["50%", "55%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="用户年龄结构分布", pos_left="center"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
            )
            # .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}%"))

        )
        grid = Grid()
        grid.add(chart=pie, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

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

        return t1

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
        flow = [str(i) for i in curr_week_dict.values()]

        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "",
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_colors(['#32c5e9'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="本周客流波动", pos_left="center"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "星期", type_="category", boundary_gap=False),
            )
        )

        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid 

    def day_line(month, day_dict) -> Line:
        day = list(day_dict.keys())
        flow = [str(j) for j in day_dict.values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "",
                y_axis=flow,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_colors(['#fb7293'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="本月客流波动", pos_left="center"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "日期", type_="category", boundary_gap=False),
            )
        )
        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

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

    def user_month_line(month_dict) -> Line:
        month = [i for i in month_dict.keys()]
        flow = [str(i) for i in month_dict.values()]
        
        line = (
            Line()
            .add_xaxis(xaxis_data = month)
            .add_yaxis(
                series_name= "",
                y_axis=flow,  
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="各月出行次数分布", pos_left="cenetr"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "出行数/次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "月份", type_="category", boundary_gap=False),
            )
        )

        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

    def line_pie(line, percent) -> Pie:
        '''
        返回线路流量占比图表
        '''
        pie = (
            Pie()
            .add(
                series_name="流量占比",
                data_pair=[list(i) for i in zip(line, percent)],
                radius= [40, 110],
                rosetype="area",
            )
            .set_colors(['#37a2da','#32c5e9','#9fe6b8','#ffdb5c','#ff9f7f','#fb7293','#e7bcf3','#8378ea'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="线路流量占比", pos_left='center'),
                legend_opts=opts.LegendOpts(is_show=False),
                tooltip_opts=opts.TooltipOpts(trigger='item', formatter="{a} <br/>{b} : {c} ({d}%)"),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}%"))

        )
        grid = Grid()
        grid.add(chart=pie, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid
    
    def pred_month_line(month_dict, month) -> Line:
        '''
        绘制单月整体预测客流分布
        返回一个Line图表
        '''
        day = [i for i in month_dict.keys()]
        flow = [str(j) for j in month_dict.values()]
        line = (
            Line()
            .add_xaxis(xaxis_data = day)
            .add_yaxis(
                series_name= "",
                y_axis=flow,
                # is_smooth=True,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_colors(['#58D5FF'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="{}月整体客流波动".format(month), pos_left="center"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量/人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(name = "日期", type_="category", boundary_gap=False),
            )
            # .render('./test.html')
        )
        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

    def pred_week_line(week_dict) -> Line:
            '''
            绘制本周预测客流分布
            返回一个Line图表
            '''
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周末']
            flow = [str(i) for i in week_dict.values()]
     
            line = (
                Line()
                .add_xaxis(xaxis_data = weekday)
                .add_yaxis(
                    series_name= "",
                    y_axis=flow,
                    label_opts=opts.LabelOpts(is_show=False),
                    is_smooth=True
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="本周客流分布", pos_left="center"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis"),
                    yaxis_opts=opts.AxisOpts(
                        name = "客流量/人次",
                        type_="value",
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                    ),
                    xaxis_opts=opts.AxisOpts(name = "星期", type_="category", boundary_gap=False),
                )
                # .render('./test.html')
            )
            grid = Grid()
            grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

            return grid

    def hour_line(hour_list, hour_flow) -> Line:
        if len(hour_flow) == 0:
            hour_flow = [0] * len(hour_list)
        line = (
            Line()
            .add_xaxis(xaxis_data = hour_list)
            .add_yaxis(
                series_name = "",
                y_axis = hour_flow,
                markpoint_opts=opts.MarkPointOpts(data=[
                    opts.MarkPointItem(type_="min", itemstyle_opts=opts.ItemStyleOpts(color ='#E271DE')),
                    opts.MarkPointItem(type_="max", itemstyle_opts=opts.ItemStyleOpts(color ='red'))
                ]),
                # is_smooth=True
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_colors(['#F8456B'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="当天小时客流分布", pos_left="center"),
                yaxis_opts=opts.AxisOpts(
                    name = "客流量 /人次",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True,
                        linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                ),
                xaxis_opts=opts.AxisOpts(name = "/时", type_="category", boundary_gap=False),
                
            )
            # .render("line_markpoint.html")
        )
        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

    def eval_radar() -> Radar:
        data = [{"value": [0.8, 0.6, 0.9, 0.5, 0.7], "name": "交通拥堵系数"}]

        radar = (
            Radar(init_opts=opts.InitOpts(width="1280px", height="720px", bg_color="#fff"))
            .add_schema(
                schema=[
                    opts.RadarIndicatorItem(name="高峰拥堵指数", max_=1),
                    opts.RadarIndicatorItem(name="高峰客流占比", max_=1),
                    opts.RadarIndicatorItem(name="高峰时间占比", max_=1),
                    opts.RadarIndicatorItem(name="不均衡系数", max_=1),
                    opts.RadarIndicatorItem(name="满载率", max_=1),
                ],
                splitarea_opt=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            )

            .add(
                series_name="",
                data=data,
                linestyle_opts=opts.LineStyleOpts(color="#CD0000"),
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
      
            # .render("basic_radar_chart.html")  
        )

        grid = Grid()
        grid.add(chart=radar, grid_opts=opts.GridOpts(pos_left="15%"))
        return grid

    def sta_age_pie(age, percent) -> Pie:
        '''
        绘制年龄结构分布图
        返回一个饼状图
        '''
        pie = (
            Pie()
            .add(
                "",
                [list(i) for i in zip(age, percent)],
                center=["50%", "60%"],
                radius = ['35%', '60%']
            )
            .set_colors( ['#58D5FF', '#73ACFF', '#FDD56A', '#FDB36A', '#FD866A'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="用户年龄结构分布", pos_left="center"),
                legend_opts=opts.LegendOpts(pos_right="0%", pos_top="5%",orient="vertical",
                    item_width=12, item_height=12, legend_icon="circle"),
                tooltip_opts=opts.TooltipOpts(formatter="{b} : {c}%")
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        )
        grid = Grid()
        grid.add(chart=pie, grid_opts=opts.GridOpts(pos_bottom="5%"))

        return grid
    
    def sta_schedule_line(hour_list, volunteer, worker) -> Line:
        line = (
            Line()
            .add_xaxis(xaxis_data = hour_list)
            .add_yaxis(
                series_name = "志愿者",
                y_axis = volunteer,
                markpoint_opts=opts.MarkPointOpts(data=[
                    opts.MarkPointItem(type_="min", itemstyle_opts=opts.ItemStyleOpts(color ='#F8456B')),
                    opts.MarkPointItem(type_="max", itemstyle_opts=opts.ItemStyleOpts(color ='#F8456B'))
                ]),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(
                series_name = "工作人员",
                y_axis = worker,
                markpoint_opts=opts.MarkPointOpts(data=[
                    opts.MarkPointItem(type_="min", itemstyle_opts=opts.ItemStyleOpts(color ='#E271DE')),
                    opts.MarkPointItem(type_="max", itemstyle_opts=opts.ItemStyleOpts(color ='#E271DE'))
                ]),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_colors(['#F8456B', '#E271DE'])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="地铁人员调度比例", pos_left="center", pos_top="0%"),
                yaxis_opts=opts.AxisOpts(
                    name = "百分比 %",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True,
                        linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                ),
                xaxis_opts=opts.AxisOpts(name = "/时", type_="category", boundary_gap=False),
                legend_opts=opts.LegendOpts(pos_top="10%")
            )
            # .render("line_markpoint.html")
        )
        grid = Grid()
        grid.add(chart=line, grid_opts=opts.GridOpts(pos_bottom="10%"))

        return grid

if __name__ == '__main__':
    chartapi = ChartApi
    chartapi.radar()
    # hour_list = ['%s' % i for i in range(6, 22, 1)]
    # hour_flow = [str(random.randint(50,100)) for i in range(6, 22, 1)]
    # chartapi.hour_line(hour_list, hour_flow)
    # predict_api=PredictApi()
    # month_dict=predict_api.get_month_flow()
    # chartapi.single_month_line(month_dict,'2020-07')
    # week_dict=predict_api.get_week_flow()
    # chartapi.single_week_line(week_dict,'2020-07')