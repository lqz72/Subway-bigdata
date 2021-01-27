from DataSource import *

def get_age_structure():
    '''
    获取年龄结构 返回一个元组 分别为年龄段 和 对应的百分比
    '''
    percent = []
    label = ["0-17岁", "18-40岁", "41—65岁", "大于66岁"]

    age_dict = DataSource().get_age_data()

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
        percent.append((val * 100) / all_num)

    return label, percent


print(get_age_structure())