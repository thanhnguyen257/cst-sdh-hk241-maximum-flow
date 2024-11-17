from collections import deque
import random

class EdmondsKarp:
    #Apply BFS in graph
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

    #Edmonds-Karp
    def run_edmonds_karp(self, capacity_matrix, source, sink):
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

if __name__ == "__main__":
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

    import pickle
    with open('database/maximum_flow_data.pickle', 'rb') as f:
        loaded_data = pickle.load(f)
    capacity_matrix = loaded_data['adj_matrix']
    n = len(capacity_matrix)
    source = 4
    sink = 2

    #Print Capacity Matrix
    print("Capacity Matrix:")
    for row in capacity_matrix:
        print(row)

    #Run algorithm
    edmonds_karp = EdmondsKarp()
    max_flow, paths = edmonds_karp.run_edmonds_karp(capacity_matrix, source, sink)
    print("The maximum possible flow is:", max_flow)

    print("\nAugmenting paths found:")
    print(paths)
    for i, (path, flow) in enumerate(paths, 1):
        print(f"Path {i}: {' -> '.join(f'{u}->{v}' for u, v in path)} with flow {flow}")
