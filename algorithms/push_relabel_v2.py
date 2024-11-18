from collections import deque
import random
import heapq

dict_map = {} # Từ điển ma trận nếu xài edges

def convert_edges_to_matrix(edges):
    """Chuyển đổi danh sách các cạnh thành ma trận kề"""
    # Xây dựng từ điển
    for edge in edges:
        u, v, cap = edge
        if u not in dict_map:
            n = len(dict_map)
            dict_map[u] = n
        if v not in dict_map:
            n = len(dict_map)
            dict_map[v] = n

    length = len(dict_map) # Số điểm trong đồ thị
    capacity = [[0]*length for i in range(length)] # Khởi tạo ma trận lưu trữ
    
    # Tạo ma trận
    for edge in edges:
        u, v, cap = edge
        i = dict_map[u]
        j = dict_map[v]
        capacity[i][j] = cap
    return capacity

def convert_matrix_to_edges(matrix):
    """Chuyển đổi ma trận thành danh sách các cạnh"""
    reversed_dict_map = {v: k for k, v in dict_map.items()} # Đảo ngược từ điển
    length = len(matrix) # Số điểm trong đồ thị
    edges = [] # Khởi tạo danh sách các cạnh
    
    # Xây dựng danh sách các cạnh
    for i in range(length):
        for j in range(length):
            if matrix[i][j] > 0:
                edges.append((i,j,matrix[i][j]))
    return edges

class PushRelabel:
    def __init__(self, n, source, sink, capacity):
        """
        Khởi tạo đồ thị với các thông số ban đầu:
        - n: Số đỉnh trong đồ thị.
        - source: Đỉnh nguồn.
        - sink: Đỉnh đích.
        - capacity: Ma trận dung lượng của đồ thị, trong đó capacity[u][v] là dung lượng của cạnh từ u đến v.
        """
        self.n = n                # Số đỉnh
        self.source = source      # Đỉnh nguồn
        self.sink = sink          # Đỉnh đích
        self.capacity = capacity  # Dung lượng của các cạnh
        self.flow = [[0] * n for _ in range(n)]  # Lưu lượng trên các cạnh (ban đầu là 0) ma trận nxn
        self.excess = [0] * n     # Lưu lượng dư thừa của mỗi đỉnh
        self.height = [0] * n     # Chiều cao (nhãn) của mỗi đỉnh
    
    def initialize_preflow(self):
        """Khởi tạo preflow từ đỉnh nguồn"""
        self.height[self.source] = self.n  # Đặt chiều cao của nguồn bằng số đỉnh
        for v in range(self.n):
            if self.capacity[self.source][v] > 0:
                self.flow[self.source][v] = self.capacity[self.source][v]
                self.flow[v][self.source] = -self.flow[self.source][v]
                self.excess[v] = self.capacity[self.source][v]
                self.excess[self.source] -= self.capacity[self.source][v]
    
    def push(self, u, v):
        """Thực hiện thao tác đẩy luồng từ u đến v"""
        delta = min(self.excess[u], self.capacity[u][v] - self.flow[u][v])
        self.flow[u][v] += delta
        self.flow[v][u] -= delta
        self.excess[u] -= delta
        self.excess[v] += delta

    def relabel(self, u):
        """Gán lại chiều cao cho đỉnh u khi u không đáp ứng"""
        min_height = float('Inf')
        for v in range(self.n):
            if self.capacity[u][v] - self.flow[u][v] > 0:
                min_height = min(min_height, self.height[v])
        self.height[u] = min_height + 1

    def discharge(self, u):
        """Giải phóng lưu lượng dư thừa của đỉnh u"""
        while self.excess[u] > 0:
            pushed = False
            for v in range(self.n):
                if self.capacity[u][v] - self.flow[u][v] > 0 and self.height[u] > self.height[v]:
                    self.push(u, v)
                    pushed = True
                    if self.excess[u] == 0:
                        break
            if not pushed:
                self.relabel(u)
    
    def max_flow(self):
        """Tính toán lưu lượng cực đại từ nguồn đến đích"""
        self.initialize_preflow()
        active = [u for u in range(self.n) if u != self.source and u != self.sink]

        i = 0
        while i < len(active):
            u = active[i]
            old_height = self.height[u]
            self.discharge(u)
            if self.height[u] > old_height:
                active.insert(0, active.pop(i))  # Di chuyển đỉnh u lên đầu danh sách
                i = 0
            else:
                i += 1
        
        return self.flow
    
    """Apply BFS in graph"""
    def bfs(self, graph, source, sink, parent):
        visited = [False] * len(graph)  #all vertices are not visited
        queue = deque([source])
        visited[source] = True  #visit <source>

        while queue:
            u = queue.popleft()                      #pick vertex = u from queue

            for v, capacity in enumerate(graph[u]):  #check neighbor of u -> vertex v and edge capacity
                if not visited[v] and capacity > 0:  #not visited -> available capacity
                    queue.append(v)                  #add v to queue
                    visited[v] = True                #check visit vertex v
                    parent[v] = u                    #set parent of v is u
                    if v == sink:                    #Reach the sink -< full path -> return True
                        return True

        return False

    """trace back and get path found by BFS"""
    def get_path(self, parent, source, sink):
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append((u, v))  #store edge as (u, v)
            v = u
        path.reverse()           #reverse to get the path from source to sink
        return path

    def edmonds_karp(self, capacity_matrix, source, sink):
        n = len(capacity_matrix)
        graph = [row[:] for row in capacity_matrix]    #Initial residual graph is the same as capacity matrix
        parent = [-1] * n                              #store parent to trace back
        max_flow = 0
        paths = []                                     #store paths

        #Increase the flow while there is a path from source to sink
        while self.bfs(graph, source, sink, parent):
            # Find the maximum flow through the path by using BFS
            path_flow = float(-1)
            v = sink
            while v != source:
                u = parent[v]
                if (path_flow < 0): path_flow = graph[u][v]
                else: path_flow = min(path_flow, graph[u][v])    #find bottleneck capacity
                v = u

            # Update residual capacities of the edges and reverse edges along the path
            v = sink
            while v != source:
                u = parent[v]
                graph[u][v] -= path_flow      #Decrease flow in forward path
                graph[v][u] += path_flow      #Increase flow in backward path
                v = u

            #Increase maxflow with the path_flow
            max_flow += path_flow

            path = self.get_path(parent, source, sink)
            paths.append((path, path_flow))    #Store path and its bottleneck flow

        return max_flow, paths

if __name__ == '__main__':
    # Số đỉnh
    n = 7
    source = 0
    sink = 6

    # Nếu đầu vào là dạng edges (A, B, 1),....
    edges = [
        ('A', 'B', 4),
        ('A', 'C', 5),
        ('A', 'D', 2),
        ('B', 'C', 7),
        ('B', 'D', 3),
        ('B', 'E', 6),
        ('C', 'D', 6),
        ('C', 'E', 8),
        ('C', 'F', 4),
        ('D', 'E', 6),
        ('D', 'F', 5),
        ('D', 'G', 3),
        ('E', 'F', 2),
    ]
    capacity = convert_edges_to_matrix(edges)

    # Nếu đầu vào là dạng capacity
    """Tạo ma trận dung lượng ngẫu nhiên cho đồ thị với các cạnh có dung lượng từ 0 đến 20"""
    # capacity = [[0 if i == j else random.randint(0, 20) for j in range(n)] for i in range(n)]
    capacity = [
        [0, 4, 5, 2, 0, 0, 8],
        [0, 0, 7, 3, 6, 0, 0],
        [0, 0, 0, 6, 8, 4, 6],
        [0, 0, 0, 0, 6, 5, 3],
        [0, 0, 0, 0, 0, 2, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ]
    
    import pickle
    with open('database/maximum_flow_data.pickle', 'rb') as f:
        loaded_data = pickle.load(f)
    capacity = loaded_data['adj_matrix']
    n = len(capacity)
    source = 162
    sink = 135
    pr = PushRelabel(n, source, sink, capacity)
    
    # In ra ma trận dòng chảy
    print("Flow Matrix:")
    flow =  pr.max_flow()
    # for row in flow:
    #     print(row)

    # Tổng lưu lượng là tổng lưu lượng từ nguồn đến các đỉnh kề
    max_flow = sum(flow[source][v] for v in range(n))
    print("Maximum Flow:", max_flow)
    
    # In ra ma trận đường đi
    # for i in range(n):
    #     for j in range(n):
    #         if flow[i][j] > 0:
    #             print(f"({i} -> {j}): {flow[i][j]}")
    print("Flow edges: ", convert_matrix_to_edges(flow))
    
    # Tìm các đường đi
    max_flow, paths = pr.edmonds_karp(flow, source, sink)

    print("\nAugmenting paths found:")
    for i, (path, flow) in enumerate(paths, 1):
        print(f"Path {i}: {' -> '.join(f'{u}->{v}' for u, v in path)} with flow {flow}")
