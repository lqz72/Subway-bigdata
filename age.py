# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

class Age_Structure(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(self.file_path, encoding='gb18030')

    #处理数据 返回一个字典 存放每个年龄对应的人数
    def process_data(self):
        age_list = self.df.groupby(by="出生年份").count()["用户ID"]
        age_index = [2021 - i for i in age_list.index]
        age_values = age_list.values

        # 创建一个字典用于存放 年龄分布
        age_dict = dict(zip(age_index, age_values))

        return age_dict

    #返回一个元组 存放年龄分布的百分比
    def get_structure(self):
        size = []
        label = ["0-17岁", "18-40岁", "41—65岁", "大于66岁"]

        age_dict = self.process_data()
        # 创建一个字典用于存放 年龄段分布
        temp_dict = dict.fromkeys(label, 0)
        for age in age_dict:
            if (0 < age) & (age <= 17):
                temp_dict["0-17岁"] += age_dict[age]
            elif (17 < age) & (age <= 40):
                temp_dict["18-40岁"] += age_dict[age]
            elif (40 < age) & (age <= 65):
                temp_dict["41—65岁"] += age_dict[age]
            else:
                temp_dict["大于66岁"] += age_dict[age]

        all_num = sum(list(age_dict.values()))
        for val in temp_dict.values():
            size.append((val * 100) / all_num)

        return label, size

    #绘制饼形图
    def show_pie_pic(self):
        label, size = self.get_structure()
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei为黑体
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        plt.figure(figsize=(20, 8), dpi=80)
        explode = (0, 0, 0, 0)
        plt.pie(size, explode=explode, labels=label, autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis("equal")
        plt.title("用户年龄结构分布")
        plt.legend(loc="best")
        plt.savefig("./age_pie.png")
        plt.show()

if __name__ == '__main__':
    user_file_path = "./users.csv"
    a = Age_Structure(user_file_path)
    a.show_pie_pic()