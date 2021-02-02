from DataSource import *
import pyecharts.options as opts
from pyecharts.charts import Line,Grid

'''
早晚高峰客流分析 
'''
def get_hour_flow(df):
        '''
        获取各个站点每个小时的进站/出站客流量 
        传入一个in_df 或者 out_df 
        返回值为一个字典 格式:{'station':{'hour':num,},}
        '''
        df.columns = ['名称', '时间']
        df['客流'] = 1
  
        sta_dict = {}
        sta_list = list(set(df['名称'].values))
        for sta in sta_list:
            my_df = df[df['名称'] == sta]
            my_df['时间'] = pd.to_datetime(my_df['时间']).dt.hour

            grouped = my_df.groupby(by = ['时间'], as_index = True)['客流'].sum()
            time, flow = grouped.index, grouped.values
            sta_dict[sta] = dict(zip(time, flow))

        return sta_dict

def get_peak_flow(df):
        '''
        获取各个站点在早晚高峰时的进/出客流
        传入一个in_df 或者 out_df
        返回两个字典 分别为早高峰(7-9)和晚高峰(5-7)时的客流量 
        格式: {'station':am_num}, {'station':pm_num}
        '''
        df.columns = ['名称', '时间']
        df['客流'] = 1

        sta_dict = am_dict = pm_dict = {}
        sta_list = list(set(df['名称'].values))
        for sta in sta_list:
            my_df = df[df['名称'] == sta]
            my_df['时间'] = pd.to_datetime(my_df['时间']).dt.hour

            grouped = my_df.groupby(by=['时间'])['客流'].sum()
            am_peak, pm_peak =grouped[7:10], grouped[5:8]
            am_dict[sta], pm_dict[sta] = am_peak.sum(), pm_peak.sum()

        return am_dict, pm_dict

def hour_line(in_dict, out_dict, station) ->Line:
    in_dict = in_dict[station]
    out_dict = out_dict[station]
    in_x_data = [str(i) for i in in_dict.keys()]
    out_x_data = [str(i) for i in out_dict.keys()]
    in_y_data = [str(i) for i in in_dict.values()]
    out_y_data = [str(-i) for i in out_dict.values()]
   
    c = (
        Line()
        .add_xaxis(in_x_data)
        .add_xaxis(out_x_data)
        .add_yaxis("进站客流", in_y_data, is_smooth=True)
        .add_yaxis("出站客流", out_y_data, is_smooth=True)
        .set_global_opts(title_opts=opts.TitleOpts(title="Line-smooth"))
        .render("hour_line.html")
    )
    return c

def peak_line(in_am, in_pm, out_am, out_pm) -> Line:
    x_in_am = list(in_am.keys())
    x_out_am = list(out_am.keys())
    y_in_am =[str(i/10) for i in in_am.values()]
    y_out_am = [str(i/10) for i in out_am.values()]
    y_in_pm = [str(i) for i in in_pm.values()]
    y_out_pm =[str(i) for i in out_pm.values()]
   
    l1 = (
        Line()
        .add_xaxis(xaxis_data=x_in_am)
        .add_xaxis(xaxis_data=x_out_am)
        .add_yaxis(
            series_name="进站",
            y_axis=y_in_am,
            symbol_size=8,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            is_smooth=True,
        )
        .add_yaxis(
            series_name="出站",
            y_axis=y_out_am,
            symbol_size=8,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            is_smooth=True,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="早晚高峰进出站客流分布", subtitle="数据来自锐意工厂", pos_left="center"
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=True,
                    is_realtime=True,
                    start_value=30,
                    end_value=70,
                    xaxis_index=[0, 1],
                )
            ],
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),
            ),
            yaxis_opts=opts.AxisOpts(max_=1000, name="客流量(/10人)"),
            legend_opts=opts.LegendOpts(pos_left="left"),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature={
                    "dataZoom": {"yAxisIndex": "none"},
                    "restore": {},
                    "saveAsImage": {},
                },
            ),
        )
    )

    l2 = (
        Line()
        .add_xaxis(xaxis_data=x_in_am)
        .add_xaxis(xaxis_data=x_out_am)
        .add_yaxis(
            series_name="进站",
            y_axis=y_in_pm,
            xaxis_index=1,
            yaxis_index=1,
            symbol_size=8,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            is_smooth=True,
        )
        .add_yaxis(
            series_name="出站",
            y_axis=y_out_pm,
            xaxis_index=1,
            yaxis_index=1,
            symbol_size=8,
            is_hover_animation=False,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            is_smooth=True,
        )
        .set_global_opts(
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            xaxis_opts=opts.AxisOpts(
                grid_index=1,
                type_="category",
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=True),
                position="top",
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_realtime=True,
                    type_="inside",
                    start_value=30,
                    end_value=70,
                    xaxis_index=[0, 1],
                )
            ],
            yaxis_opts=opts.AxisOpts(is_inverse=True, name="/人"),
            legend_opts=opts.LegendOpts(pos_left="20%"),
        )
    )

    (
        Grid(init_opts=opts.InitOpts(width="1024px", height="768px"))
        .add(chart=l1, grid_opts=opts.GridOpts(pos_left=50, pos_right=50, height="35%"))
        .add(
            chart=l2,
            grid_opts=opts.GridOpts(pos_left=50, pos_right=50, pos_top="55%", height="35%"),
        )
        .render('peak_flow.html')
        
    )

ds = DataSource()
in_df, out_df = ds.clean_data()
in_am, in_pm = get_peak_flow(in_df)
out_am, out_pm = get_peak_flow(out_df)
peak_line(in_am, in_pm, out_am, out_pm)


