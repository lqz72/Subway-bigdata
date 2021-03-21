from ShortestPath import *
from MysqlOS import SQLOS

def get_date_df(date):

    trips_df = SQLOS.get_trips_df()
    trips_df.drop('user_id', axis =1, inplace=True)
    trips_df.set_index('in_time', inplace=True)
    date_df = trips_df.loc[date]
    date_df.reset_index(level = 'in_time', inplace =True)
    
    return date_df

def get_line_split_flow(date, line = '1号线', flag=0):
    
    sp = ShortestPath()
    line_split = {}
    df = get_date_df(date)
    for row in df.itertuples(index = False):
        start = getattr(row, 'in_sta_name')
        end = getattr(row, 'out_sta_name')
        path = sp.get_shortest_path(start)[end]
   
        for i in range(len(path) - 1):
            split = path[i] + '-' + path[i + 1]
            if split not in line_split.keys():
                line_split[split] = 0
            else:
                line_split[split] += 1

    print(line_split)



if __name__ == '__main__':

    get_line_split_flow('2020-07-01')
