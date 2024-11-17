import random

dict_map = {}

def convert_edges_to_matrix(edges):
    for edge in edges:
        u, v, cap = edge
        if u not in dict_map:
            n = len(dict_map)
            dict_map[u] = n
        if v not in dict_map:
            n = len(dict_map)
            dict_map[v] = n

    length = len(dict_map)
    capacity = [[0]*length for i in range(length)]
    for edge in edges:
        u, v, cap = edge
        i = dict_map[u]
        j = dict_map[v]
        capacity[i][j] = cap
    return capacity

def convert_matrix_to_edges(matrix):
    reversed_dict_map = {v: k for k, v in dict_map.items()}
    length = len(dict_map)
    edges = []
    
    for i in range(length):
        for j in range(length):
            if matrix[i][j] > 0:
                edges.append((reversed_dict_map[i],reversed_dict_map[j],matrix[i][j]))
    
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
    # Tạo ma trận dung lượng ngẫu nhiên cho đồ thị với các cạnh có dung lượng từ 0 đến 20
    '''capacity = [[0 if i == j else random.randint(0, 20) for j in range(n)] for i in range(n)]
    capacity = [
        [0, 15, 14, 12, 10, 17],
        [20, 0, 1, 0, 10, 18],
        [18, 14, 0, 6, 9, 19],
        [19, 14, 20, 0, 7, 5],
        [9, 5, 17, 4, 0, 10],
        [12, 5, 18, 11, 19, 0]
    ]'''

    # Hiển thị ma trận dung lượng
    print("Capacity Matrix:")
    for row in capacity:
        print(row)

    import pickle
    with open('database/maximum_flow_data.pickle', 'rb') as f:
        loaded_data = pickle.load(f)
    capacity = loaded_data['adj_matrix']
    n = len(capacity)
    source = 4
    sink = 2
        
    pr = PushRelabel(n, source, sink, capacity)
    
    # In ra ma trận dòng chảy
    print("Flow Matrix:")
    flow =  pr.max_flow()
    for row in flow:
        print(row)

    # Tổng lưu lượng là tổng lưu lượng từ nguồn đến các đỉnh kề
    max_flow = sum(flow[source][v] for v in range(n))
    print("Maximum Flow:", max_flow)
    
    # In ra ma trận đường đi
    for i in range(n):
        for j in range(n):
            if flow[i][j] > 0:
                print(f"({i} -> {j}): {flow[i][j]}")
    print("Flow edges: ", convert_matrix_to_edges(flow))
