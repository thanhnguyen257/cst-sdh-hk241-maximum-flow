def convert_matrix(edges):
    dict_1 = {}
    for edge in edges:
        u, v, cap = edge
        if u not in dict_1:
            n = len(dict_1)
            dict_1[u] = n
        if v not in dict_1:
            n = len(dict_1)
            dict_1[v] = n

    length = len(dict_1)
    capacity = [[0]*length for i in range(length - 1)]
    for edge in edges:
        u, v, cap = edge
        i = dict_1[u]
        j = dict_1[v]
        capacity[i][j] = cap
        
    print("Capacity Matrix:")
    for row in capacity:
        print(row)
    return capacity