from MysqlOS import SQLOS
import time
import json
import os

abs_path = os.path.abspath(os.path.dirname(__file__))


class Vertex:
    def __init__(self, key):
        self.id = key
        self.nextarc = {}

    def __str__(self):
        return str(self.id) + 'nextarc: ' + str([x.id for x in self.nextarc])

    def add_neighbor(self, adj, weight=1):
        self.nextarc[adj] = weight

    def get_id(self):
        return self.id

    def get_nextarc(self):
        return self.nextarc.keys()

    def get_nextarc_id(self):
        return [arc.id for arc in self.nextarc.keys()]

    def get_weight(self, adj):
        return self.nextarc[adj]


class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.vert_num = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def __contains__(self, key):
        return key in self.vert_dict

    def add_vertex(self, key):
        self.vert_num += 1
        new_vertex = Vertex(key)
        self.vert_dict[key] = new_vertex

        return new_vertex

    def add_edge(self, head, tail, weight):
        if head not in self.vert_dict:
            self.add_vertex(head)
        if tail not in self.vert_dict:
            self.add_vertex(tail)

        self.vert_dict[head].add_neighbor(self.vert_dict[tail], weight)
        self.vert_dict[tail].add_neighbor(self.vert_dict[head], weight)

    def get_vertex(self, key):
        if key in self.vert_dict:
            return self.vert_dict[key]
        else:
            return None

    def get_vertexs(self):
        return self.vert_dict.keys()


class ShortestPath():
    """用于求解最短路径
    """

    def __init__(self):
        self.graph = Graph()

        # 初始化graph
        link_list = ShortestPath.load_link_data()
        for link in link_list:
            self.graph.add_edge(link['head'], link['tail'], 1)

    def load_link_data():
        """获取站点连接数据
        """
        with open(abs_path + '/json/links.json', 'r', encoding='utf-8') as f:
            link_list = json.load(f)

        return link_list

    def get_link_json():
        abs_path = os.path.abspath(os.path.dirname(__file__))
        with open(abs_path + '/json/links.json', 'r', encoding='utf-8') as f:
            links = json.load(f)
            link_list = []
            for link in links:
                link_list.append(
                    {
                        'head': link['source'],
                        'tail': link['target']
                    }
                )

            with open(abs_path + '/json/links.json', 'w', encoding='utf-8') as ff:
                json.dump(link_list, ff)

    def Dijkstra(self, graph, start):
        """获取最短路径 迪杰斯特拉算法
            Params:
            -------
            graph: Graph Object

            start: 字符串 站点名称

            Returns:
            --------
            path: 字典 包含各个站点在最短路径中的前一个站点
        """

        # 初始化
        flag = dict.fromkeys(graph.get_vertexs(), 0)  # 标志是否已找到最短路径
        table = dict.fromkeys(graph.get_vertexs(), 0)  # 记录从源点到某站点的路径权值和
        path = dict.fromkeys(graph.get_vertexs(), start)  # 记录某站点在最短路径中的前一个站点

        # 遍历图的所有结点
        for v in graph:
            # 如果该结点的id等于源点 自身到自身的路径权值和显然为0
            if v.id == start:
                table[v.id] = 0
            else:
                # 如果源点与该结点邻接 则直接等于权值 否则等于inf
                table[v.id] = graph.vert_dict[start].nextarc.get(v, float('inf'))

        # 将源点flag置为1
        flag[start] = 1

        # 主循环 由于不需要求自身到自身的路径 所以循环数-1
        for i in range(1, graph.vert_num):
            min = float('inf')

            # 遍历所有结点的id
            for w in graph.vert_dict:
                # 寻找离源点最近的点 即权值最小
                if flag[w] == 0 and table[w] < min:
                    k = w
                    min = table[w]

            flag[k] = 1

            # 修正当前从k到w的最短路径
            for w in graph.vert_dict[k].get_nextarc():

                vert_height = graph.vert_dict[k].nextarc[w]
                if flag[w.id] == 0 and (min + vert_height) < table[w.id]:
                    # 说明找到了更短的路径
                    table[w.id] = min + vert_height
                    path[w.id] = k

        return path

    def get_one_path(self, path, start, end):
        """
        根据path字典获取起始站点和终点之间的最短路径
        """
        path_list = [end, ]

        if (start != end):
            pre = path.get(end)

            while pre != start:
                path_list.append(pre)
                end = pre
                pre = path.get(end)

            path_list.append(pre)
            path_list.reverse()

        return path_list

    def get_shortest_path(self, start):
        """获取以某个站点为源点的最短路径
        """
        path_dict = {}

        # 使用迪杰斯特拉算法求出path字典
        path = self.Dijkstra(self.graph, start)

        for end in self.graph.get_vertexs():
            # 如果源点和终点相等
            if start == end:
                continue

            # 获取一条最短路径
            path_list = self.get_one_path(path, start, end)
            path_dict[end] = path_list

        return path_dict

    def get_all_shortest_path(self):
        """获取所有最短路径
        """
        path_dict = {}
        # 遍历图中所有结点
        for start in self.graph.get_vertexs():
            # 使用迪杰斯特拉算法求出path字典
            path = self.Dijkstra(self.graph, start)

            path_dict[start] = {}
            for end in self.graph.get_vertexs():
                # 如果源点和终点相等
                if start == end:
                    continue

                # 获取一条最短路径
                path_list = self.get_one_path(path, start, end)
                path_dict[start][end] = path_list

            with open(abs_path + '/json/path/' + start + '.json', 'w', encoding='utf-8') as f:
                json.dump(path_dict[start], f)

        return path_dict
