from PredictResult import PredictApi
pred_api = PredictApi()


def get_peek_hour(date):
    """
    获取每日的高峰时间
    """
    try:
        hour_flow = pred_api.get_hour_flow(date,'all')
        hour_flow_sort = sorted(hour_flow)
        list_len = hour_flow.__len__()
        peek_flow = hour_flow_sort[int(list_len*0.8)-1]
        peek_hour=  0
        for i in range(0,list_len-1):
            if hour_flow[i] >= peek_flow and hour_flow[i+1] >= peek_flow:
                peek_hour += 1
        return peek_hour
    except Exception as e:
        print('Error:', e)

def get_peek_time(date):
    """
    获取每日的高峰时间段
    """
    try:
        hour_flow = pred_api.get_hour_flow(date,'all')
        hour_flow_sort = sorted(hour_flow)
        list_len = hour_flow.__len__()
        peek_flow = hour_flow_sort[int(list_len*0.8)-1]
        peek_time = []
        for i in range(0,list_len-1):
            if hour_flow[i] >= peek_flow and hour_flow[i+1] >= peek_flow:
                peek_time.append(i)
        return peek_time
    except Exception as e:
        print('Error:', e)

def get_uneven_flow(date):
    """
    客流的不均衡系数
    """
    day_sta_flow = pred_api.get_day_sta_flow(date)
    sta_flow=[]
    for value in day_sta_flow.values():
        sta_flow.append(value)
    top = 0
    top += sta_flow[0]+sta_flow[1]+sta_flow[2]+sta_flow[3]+sta_flow[4]
    low = 0
    low += sta_flow[-1]+sta_flow[-2]+sta_flow[-3]+sta_flow[-4]+sta_flow[-5]
    proportion = top/low
    return proportion

def get_flow_congestion(date):
    """
    交通拥挤度
    """
    line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']
    line_dict = dict.fromkeys(line_list,0)
    for line in line_list:
        line_dict[line] = pred_api.get_hour_flow(date, 'all', line)
    full = 100
    count = [0,0,0,0,0,0,0,0]
    line = [0,0,0,0,0,0,0,0]
    for i in line_dict['1号线']:
        if i >= 100:
            line[0] += i
            count[0] += 1
    for i in line_dict['2号线']:
        if i >= 100:
            line[1] += i
            count[1] += 1
    for i in line_dict['3号线']:
        if i >= 100:
            line[2] += i
            count[2] += 1
    for i in line_dict['4号线']:
        if i >= 100:
            line[3] += i
            count[3] += 1
    for i in line_dict['5号线']:
        if i >= 100:
            line[4] += i
            count[4] += 1
    for i in line_dict['10号线']:
        if i >= 100:
            line[5] += i
            count[5] += 1
    for i in line_dict['11号线']:
        if i >= 100:
            line[6] += i
            count[6] += 1
    for i in line_dict['12号线']:
        if i >= 100:
            line[7] += i
            count[7] += 1
    ratio = 0
    num = 0
    for i in range(0,line.__len__()):
        if count[i] != 0:
            ratio += line[i]/ (100 * count[i])
            num += 1
    ratio /= num
    return ratio

def get_peek_flow_congestion(date):
    """
    高峰拥堵指数
    """
    peek_time = get_peek_time(date)
    line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']
    line_dict = dict.fromkeys(line_list, 0)
    for line in line_list:
	    line_dict[line] = pred_api.get_hour_flow(date, 'all', line)
    line = [0,0,0,0,0,0,0,0]
    for i in range(0,line_dict['1号线'].__len__()):
        if i in peek_time:
            line[0] += line_dict['1号线'][i]
    for i in range(0,line_dict['2号线'].__len__()):
        if i in peek_time:
            line[1] += line_dict['2号线'][i]
    for i in range(0,line_dict['3号线'].__len__()):
        if i in peek_time:
            line[2] += line_dict['3号线'][i]
    for i in range(0,line_dict['4号线'].__len__()):
        if i in peek_time:
            line[3] += line_dict['4号线'][i]
    for i in range(0,line_dict['5号线'].__len__()):
        if i in peek_time:
            line[4] += line_dict['5号线'][i]
    for i in range(0,line_dict['10号线'].__len__()):
        if i in peek_time:
            line[5] += line_dict['10号线'][i]
    for i in range(0,line_dict['11号线'].__len__()):
        if i in peek_time:
            line[6] += line_dict['11号线'][i]
    for i in range(0,line_dict['12号线'].__len__()):
        if i in peek_time:
            line[7] += line_dict['12号线'][i]
    full = 100 * peek_time.__len__()
    ratio = 0
    for i in range(0,line.__len__()):
        ratio += line[i]/full
    ratio /= peek_time.__len__()
    return ratio

def get_line_capacity_ratio(date):
    """
    线路满载率
    """
    line_list = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线']
    line_dict = dict.fromkeys(line_list, 0)
    for line in line_list:
	    line_dict[line] = pred_api.get_hour_flow(date, 'all', line)
    full = 1600
    line1 = 0
    for i in line_dict['1号线']:
        line1 += i
    line2 = 0
    for i in line_dict['2号线']:
        line2 += i
    line3 = 0
    for i in line_dict['3号线']:
        line3 += i
    line4 = 0
    for i in line_dict['4号线']:
        line4 += i
    line5 = 0
    for i in line_dict['5号线']:
        line5 += i
    line10 = 0
    for i in line_dict['10号线']:
        line10 += i
    line11 = 0 
    for i in line_dict['11号线']:
        line11 += i
    line12 = 0
    for i in line_dict['12号线']:
        line12 += i
    ratio = 0
    ratio += line1/full + line2/full + line3/full + line4/full + line5/full + line10/full + line11/full + line12/full
    ratio /= 8
    return ratio

if __name__ == "__main__":
    print(get_peek_hour('2020-07-22'))  # ok
    print(get_uneven_flow('2020-07-22'))  # ok 
    print(get_line_capacity_ratio('2020-07-22')) # ok
    print(get_flow_congestion('2020-07-22'))   # ok
    print(get_peek_flow_congestion('2020-07-22'))   # ok
