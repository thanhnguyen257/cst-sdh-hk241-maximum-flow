import networkx as nx
import heapq

def create_graph_from_matrices(capacity_adj_matrix, cost_adj_matrix):
    G = nx.DiGraph()

    n = capacity_adj_matrix.shape[0]

    for i in range(n):
        for j in range(n):
            if capacity_adj_matrix[i, j] > 0:
                G.add_edge(i, j, capacity=capacity_adj_matrix[i, j], cost=cost_adj_matrix[i, j])

    return G

def dijkstra_shortest_path(cost_matrix, source):
    cost_matrix = [[float(value) for value in row] for row in cost_matrix]
    n = len(cost_matrix)
    for i in range(n):
        for j in range(n):
            if i != j and cost_matrix[i][j] == 0:
                cost_matrix[i][j] = float('inf')
    dist = [float('inf')] * n
    parent = [None] * n
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        current_dist, u = heapq.heappop(heap)
        if current_dist > dist[u]:
            continue
        for v in range(n):
            if cost_matrix[u][v] < float('inf'):
                reduced_cost = cost_matrix[u][v]
                if dist[u] + reduced_cost < dist[v]:
                    dist[v] = dist[u] + reduced_cost
                    parent[v] = u
                    heapq.heappush(heap, (dist[v], v))
    return parent, dist

class SuccessiveShortestPath:
    def ssp_min_cost_flow(self, graph, supply, source, sink):
        flow = { (u, v): 0 for u, v in graph.edges }
        residual_graph = graph.copy()
        total_flow = 0
        total_cost = 0
        potential = {node: 0 for node in graph.nodes}
        flow_paths = []

        def ensure_reverse_edge(u, v):
            if (v, u) not in flow:
                flow[(v, u)] = 0

        def shortest_path(residual, source):
            dist = {node: float('inf') for node in residual.nodes}
            dist[source] = 0
            parent = {node: None for node in residual.nodes}
            heap = [(0, source)]

            while heap:
                current_dist, u = heapq.heappop(heap)
                if current_dist > dist[u]:
                    continue
                for v in residual.neighbors(u):
                    capacity = residual[u][v]['capacity'] - flow.get((u, v), 0)
                    if capacity > 0:
                        reduced_cost = residual[u][v]['cost'] + potential[u] - potential[v]
                        if dist[u] + reduced_cost < dist[v]:
                            dist[v] = dist[u] + reduced_cost
                            parent[v] = u
                            heapq.heappush(heap, (dist[v], v))

            return parent, dist

        while any(supply[node] > 0 for node in supply):
            source = next(node for node in supply if supply[node] > 0)
            sink = next(node for node in supply if supply[node] < 0)

            parent, dist = shortest_path(residual_graph, source)
            if parent[sink] is None:
                break

            path = []
            node = sink
            while node != source:
                path.append((parent[node], node))
                node = parent[node]
            path.reverse()

            delta = min(
                supply[source],
                -supply[sink],
                min(residual_graph[u][v]['capacity'] - flow.get((u, v), 0) for u, v in path)
            )

            for u, v in path:
                ensure_reverse_edge(u, v)
                flow[(u, v)] += delta
                flow[(v, u)] -= delta
                if (u, v) in residual_graph.edges:
                    residual_graph[u][v]['capacity'] -= delta
                if (v, u) in residual_graph.edges:
                    residual_graph[v][u]['capacity'] += delta

            supply[source] -= delta
            supply[sink] += delta

            total_cost += delta * sum(residual_graph[u][v]['cost'] for u, v in path)
            total_flow += delta

            flow_paths.append((path, delta))

            for node in residual_graph.nodes:
                if dist[node] < float('inf'):
                    potential[node] += dist[node]

        return flow_paths, total_flow

if __name__ == '__main__':
    import pickle
    with open('database/maximum_flow_data.pickle', 'rb') as f:
        loaded_data = pickle.load(f)

    capacity_adj_matrix = loaded_data['capacity_adj_matrix']
    cost_adj_matrix = loaded_data['cost_adj_matrix']
    source = 87
    sink = 4
    n = capacity_adj_matrix.shape[0]
    supply = {i: 0 for i in range(n)}
    supply[source] = float('inf')
    supply[sink] = -float('inf')

    G = create_graph_from_matrices(capacity_adj_matrix, cost_adj_matrix)

    ssp = SuccessiveShortestPath()
    flow_paths, total_flow = ssp.ssp_min_cost_flow(G, supply, source, sink)
    print(f"Flow paths: {flow_paths}")
    print(f"Max flow: {total_flow}")

    parent, dist = dijkstra_shortest_path(cost_adj_matrix, source)
    print(parent)
    path = []
    if parent[sink] is not None:
        node = sink
        while node != source:
            path.append((parent[node], node))
            node = parent[node]
        path.reverse()
    print(f"Shortest path: {path}")
