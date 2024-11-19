import random

class ForkFulkerson:
    def dfs(self, graph, source, sink, parent):
        visited = [False] * len(graph)
        stack = [source]

        while stack:
            u = stack.pop()
            for v, capacity in enumerate(graph[u]):
                if not visited[v] and capacity > 0:  
                    stack.append(v)
                    visited[v] = True
                    parent[v] = u
                    if v == sink:  
                        return True
        return False

    #trace back and get path found by BFS
    def get_path(self, parent, source, sink):
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append((u, v))  #store edge as (u, v)
            v = u
        path.reverse()           #reverse to get the path from source to sink
        return path

    #Fork-Fulkerson
    def run_fork_fulkerson(self, capacity_matrix, source, sink):
        n = len(capacity_matrix)
        graph = [row[:] for row in capacity_matrix]    #Initial residual graph is the same as capacity matrix
        parent = [-1] * n                              #store parent to trace back
        max_flow = 0
        paths = []                                     #store paths

        #Increase the flow while there is a path from source to sink
        while self.dfs(graph, source, sink, parent):
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
    #capacity matrix test
    capacity_matrix = [
        [0, 10, 10, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 4, 8, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 9, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 10, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 10, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 10, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 10, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 10],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    #random capacity matrix
    n=10
    capacity_matrix1 = [[0 if i == j else random.randint(0, 20) for j in range(n)] for i in range(n)]

    #source and sink
    source = 0
    sink = 9

    #Print Capacity Matrix
    print("Capacity Matrix:")
    for row in capacity_matrix:
        print(row)

    #Run algorithm
    max_flow, paths = ForkFulkerson().run_fork_fulkerson(capacity_matrix, source, sink)
    print("The maximum possible flow is:", max_flow)

    print("\nAugmenting paths found:")
    for i, (path, flow) in enumerate(paths, 1):
        print(f"Path {i}: {' -> '.join(f'{u}->{v}' for u, v in path)} with flow {flow}")
