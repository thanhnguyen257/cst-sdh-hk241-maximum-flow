from collections import deque
import copy
def ford_fulkerson(adj_matrix, source, sink):
    n = len(adj_matrix)
    residual = copy.deepcopy(adj_matrix)
    max_flow = 0
    paths = []

    def dfs():
        """Depth-First Search to find a path with available capacity."""
        parent = [-1] * n
        visited = [False] * n
        stack = [source]  # Use a stack for DFS
        visited[source] = True

        while stack:
            u = stack.pop()
            for v in range(n):
                if not visited[v] and residual[u][v] > 0:  # Capacity exists
                    parent[v] = u
                    visited[v] = True
                    if v == sink:
                        return parent
                    stack.append(v)
        return None

    while True:
        parent = dfs()
        if not parent:  # No augmenting path found
            break

        # Find the bottleneck capacity (minimum capacity along the path)
        path_flow = float('Inf')
        v = sink
        path = []
        while v != source:
            u = parent[v]
            if adj_matrix[u][v] > 0:
                path_flow = min(path_flow, residual[u][v])
                path.insert(0, (u, v))
            v = u

        # Update residual graph
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u

        # Record path and flow
        max_flow += path_flow
        paths.append((path, path_flow))

    return max_flow, paths


# Example usage
if __name__ == "__main__":
    adj_matrix = [
        [0, 16, 13, 0, 0, 0],  # Node 0 connections
        [0, 0, 10, 12, 0, 0],  # Node 1 connections
        [0, 4, 0, 0, 14, 0],   # Node 2 connections
        [0, 0, 9, 0, 0, 20],   # Node 3 connections
        [0, 0, 0, 7, 0, 4],    # Node 4 connections
        [0, 0, 0, 0, 0, 0],    # Node 5 connections (sink)
    ]

    source = 1
    sink = 5

    max_flow, paths = ford_fulkerson(adj_matrix, source, sink)
    print("max_flow", max_flow)
    print("paths", paths)
