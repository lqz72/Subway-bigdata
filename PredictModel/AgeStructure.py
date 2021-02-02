from DataSource import *
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.charts import Pie
from pyecharts.faker import Faker

def get_age_structure():
    '''
    获取年龄结构 返回一个元组 分别为年龄段 和 对应的百分比
    '''
    label = ["0-20岁", "21-30岁", "31-40岁", "41—50岁", "大于50岁"]
    percent  = []
    age_dict = DataSource().get_age_data()

    # 创建一个字典用于存放 年龄段分布
    temp_dict = dict.fromkeys(label, 0)
    for age in age_dict:
        if (0 < age) & (age <= 20):
            temp_dict["0-20岁"] += age_dict[age]
        elif (20 < age) & (age <= 30):
            temp_dict["21-30岁"] += age_dict[age]
        elif (30 < age) & (age <= 40):
            temp_dict["31-40岁"] += age_dict[age]
        elif (40 < age) & (age <= 50):
            temp_dict["41—50岁"] += age_dict[age]
        else:
            temp_dict["大于50岁"] += age_dict[age]

    all_num = sum(list(age_dict.values()))
    for val in temp_dict.values():
        percent.append(round(val * 100 / all_num, 2))

    return label, percent

def age_radar(age, percent) -> Radar:
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
        .render("./age_radar.html")
    )
    return c

def age_pie(age, percent) -> Pie:
    c = (
        Pie()
        .add(
            "",
            [list(i) for i in zip(age, percent)],
            center=["40%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Pie"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}%"))
        .render("./age_pie.html")
    )
    return c

# age, percent = get_age_structure()
# age_pie(age, percent)
# age_radar(age, percent)