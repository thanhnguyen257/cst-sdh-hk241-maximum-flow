from flask import Flask, render_template, send_from_directory, jsonify, request
import folium
from folium.plugins import PolyLineTextPath
import pickle
import random
import time
from algorithms.push_relabel_v2 import PushRelabel
from algorithms.edmond_karp_v3 import EdmondsKarp
from algorithms.fork_fulkerson_v1 import ForkFulkerson

app = Flask(__name__)
with open('database/maximum_flow_data.pickle', 'rb') as f:
    loaded_data = pickle.load(f)
node_dict = loaded_data['df_node_dict']
edge_dict = loaded_data['df_edge_dict']
maximum_flow = 0
runtime = 0
color_path = {0:'#FFFFFF'}

def add_return_edges(edge_dict):
    new_edges = {}

    for key, value in edge_dict.items():
        start, end = key
        return_edge_key = (end, start)

        if return_edge_key not in edge_dict and return_edge_key not in new_edges:
            return_edge = {
                'start': end,
                'end': start,
                'capacity': value['capacity'],
                'name': f'{value['name']} (WRONG WAYS)',
                'node_coordinate': value['node_coordinate'][::-1],
                'color': '#000000',
            }
            new_edges[return_edge_key] = return_edge

    edge_dict.update(new_edges)
    return edge_dict

add_return_edges(edge_dict=edge_dict)

def initialize_map(nodes=None):
    map_instance = folium.Map(location=(10.799306, 106.678383), zoom_start=13)
    if nodes is not None:
            folium.Marker([node_dict[nodes[0]]['latitude'], node_dict[nodes[0]]['longitude']]
                          , icon=folium.Icon(color='green', icon='circle', prefix='fa')
                          , popup=f"{nodes[0]}.{node_dict[nodes[0]]['name']}").add_to(map_instance)
            folium.Marker([node_dict[nodes[1]]['latitude'], node_dict[nodes[1]]['longitude']]
                          , icon=folium.Icon(color='red', icon='flag', prefix='fa')
                          , popup=f"{nodes[1]}.{node_dict[nodes[1]]['name']}").add_to(map_instance)
    return map_instance

def draw_map(map_type, nodes=None, edges=None):
    map_instance = initialize_map(nodes)
    global color_path
    if map_type == "default":
        for node_id in node_dict:
            folium.Marker([node_dict[node_id]['latitude'], node_dict[node_id]['longitude']], popup=f"{node_id}.{node_dict[node_id]['name']}").add_to(map_instance)

        # for edge_id in edge_dict:
        #     folium.PolyLine(edge_dict[edge_id]['node_coordinate'], color="blue", weight=10, opacity=0.7).add_to(map_instance)

        map_instance.save("static/default_map.html")
    elif map_type != "default" and edges is not None:

        def generate_random_color(number_of_path):
            colors = set()
            while len(colors) < number_of_path:
                color = (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255))
                if color != (255, 255, 255) and color != (255, 255, 0) and color != (255, 0, 0):
                    colors.add('#{:02x}{:02x}{:02x}'.format(*color))
            return list(colors)
        
        no_of_path = len(edges)
        colors = generate_random_color(no_of_path)
        edge_info = dict()
        min_edge_path_each = dict()
        min_edge_path_full = dict()

        # Find min capacity edge each path and edge in multiple path
        for i, paths in enumerate(edges,1):
            max_flow = paths[1]
            path = paths[0]
            for edge in path:
                if edge not in edge_info:
                    edge_info[edge] = {i:max_flow}
                else:
                    edge_info[edge][i] = max_flow

                if i in min_edge_path_each:
                    if min_edge_path_each[i][1] > edge_dict[edge]['capacity']:
                        min_edge_path_each[i] = ({edge}, edge_dict[edge]['capacity'])
                    elif min_edge_path_each[i][1] == edge_dict[edge]['capacity']:
                        min_edge_path_each[i][0].add(edge)
                else:
                    min_edge_path_each[i] = ({edge}, edge_dict[edge]['capacity'])
        
        # Find min capacity edge each path that only in one path
        for i, paths in enumerate(edges,1):
            for edge in paths[0]:
                if len(edge_info[edge]) > 1:
                    continue
                if i in min_edge_path_full:
                    if min_edge_path_full[i][1] > edge_dict[edge]['capacity']:
                        min_edge_path_full[i] = ({edge}, edge_dict[edge]['capacity'])
                    elif min_edge_path_full[i][1] == edge_dict[edge]['capacity']:
                        min_edge_path_full[i][0].add(edge)
                else:
                    min_edge_path_full[i] = ({edge}, edge_dict[edge]['capacity'])

        # Add edge line to each path map and edge line that only in one path to full map
        color_path = {0:'#FFFFFF'}
        for i, (paths, color) in enumerate(zip(edges, colors),1):
            max_flow = paths[1]
            map_path_each = initialize_map(nodes=nodes)
            color_path[i] = color
            for edge in paths[0]:
                edge_color = "#FF0000" if edge in min_edge_path_each[i][0] else color
                edge_color = edge_dict[edge]["color"] if "color" in edge_dict[edge] else edge_color
                line = folium.PolyLine(edge_dict[edge]['node_coordinate']
                                    , color=edge_color
                                    , weight=10
                                    , opacity=0.7).add_to(map_path_each)
                
                arrows = PolyLineTextPath(
                    line,
                    '   ➤   ',
                    repeat=True,
                    offset=0,
                    attributes={'fill':edge_color
                                , 'font-size':'30'}
                )
                map_path_each.add_child(arrows)

                popup_str = f"{edge_dict[edge]['name']}:{edge_dict[edge]['capacity']}"
                popup_str += f"<br>Path {i}: {max_flow}"
                popup = folium.Popup(popup_str, max_width=300)
                line.add_child(popup)

                if len(edge_info[edge]) == 1:
                    edge_color = "#FF0000" if edge in min_edge_path_full[i][0] else color
                    edge_color = edge_dict[edge]["color"] if "color" in edge_dict[edge] else edge_color
                    line = folium.PolyLine(edge_dict[edge]['node_coordinate']
                                        , color=edge_color
                                        , weight=10
                                        , opacity=0.7).add_to(map_instance)
                    
                    arrows = PolyLineTextPath(
                        line,
                        '   ➤   ',
                        repeat=True,
                        offset=0,
                        attributes={'fill':edge_color
                                    , 'font-size':'30'}
                    )
                    map_instance.add_child(arrows)
                    popup = folium.Popup(popup_str, max_width=300)
                    line.add_child(popup)

            map_path_each.save(f"maps/map_{i}.html")

        # Add edge line that is in multiple path to full map
        for  edge in edge_info:
            if len(edge_info[edge]) == 1:
                continue
            edge_color = "#FFFF00"
            edge_color = edge_dict[edge]["color"] if "color" in edge_dict[edge] else edge_color
            line = folium.PolyLine(edge_dict[edge]['node_coordinate']
                                , color=edge_color
                                , weight=10
                                , opacity=0.7).add_to(map_instance)
            
            arrows = PolyLineTextPath(
                line,
                '   ➤   ',
                repeat=True,
                offset=0,
                attributes={'fill':edge_color
                            , 'font-size':'30'}
            )
            map_instance.add_child(arrows)

            popup_str = f"{edge_dict[edge]['name']}:{edge_dict[edge]['capacity']}"
            for i in sorted(edge_info[edge].keys()):
                popup_str += f"<br>Path {i}: {edge_info[edge][i]}"
            popup = folium.Popup(popup_str, max_width=300)
            line.add_child(popup)

    map_instance.save("maps/map_full.html")

draw_map(map_type="default")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_options', methods=['GET'])
def get_options():
    data = {
        'start': [node_dict[i]['name'] for i in range(len(node_dict))],
        'destination': [node_dict[i]['name'] for i in range(len(node_dict))],
        'algorithm': ['Push–Relabel','Edmonds–Karp','Ford–Fulkerson']
    }
    return jsonify(data)

@app.route('/get_map', methods=['GET'])
def get_map():
    map_id = request.args.get('map_id')
    
    if map_id is not None:
        if  map_id == "0":
            return send_from_directory('maps', 'map_full.html')
        else:
            return send_from_directory('maps', f'map_{map_id}.html')
    
    start = int(request.args.get('start'))
    destination = int(request.args.get('destination'))
    algorithm = request.args.get('algorithm')

    capacity_matrix = loaded_data['adj_matrix'].copy()
    global maximum_flow, runtime
    
    if algorithm == "0":
        map_type = "push_relabel"
        pushrelabel = PushRelabel(len(capacity_matrix), start, destination, capacity_matrix)
        start_time = time.perf_counter()
        flow =  pushrelabel.max_flow()
        end_time = time.perf_counter()
        max_flow, paths = pushrelabel.edmonds_karp(flow, start, destination)
    elif algorithm == "1":
        map_type = "edmond_karp"
        edmonds_karp = EdmondsKarp()
        start_time = time.perf_counter()
        max_flow, paths = edmonds_karp.run_edmonds_karp(capacity_matrix, start, destination)
        end_time = time.perf_counter()
    elif algorithm == "2":
        map_type = "ford_fulkerson"
        forkfulkerson = ForkFulkerson()
        start_time = time.perf_counter()
        max_flow, paths = forkfulkerson.run_fork_fulkerson(capacity_matrix, start, destination)
        end_time = time.perf_counter()
    
    maximum_flow = max_flow
    runtime = end_time - start_time
    draw_map(map_type=map_type, nodes=(start,destination), edges=paths)
    return send_from_directory('maps', 'map_full.html')

@app.route('/get_data')
def get_data():
    global maximum_flow, runtime, color_path
    data = {
        'max_flow': str(int(maximum_flow)),
        'runtime': f"{runtime:.5f}",
        'color_path': color_path
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
