import pandas as pd
import folium

data = [
    ['Công Ty TNHH Xe Máy Hoàng Việt', '10.7622766, 106.6567513'],
    # ['','10.762187, 106.656977'],
    # ['','10.767681, 106.667101'],
    # ['','10.767977, 106.667471'],
    # ['','10.778245, 106.645464'],
    # ['','10.775136, 106.647752'],
    # ['','10.780906, 106.643646'],
    ['Satra Mart', '10.7682508, 106.6673806'],
]
# 10.803246, 106.635960
df = pd.DataFrame(data, columns=['Node', 'Location'])
center_point = df['Location'].tolist()[0].split(',')
initial_map = folium.Map(location=(center_point[0], center_point[1]), zoom_start=16)
for node, location in zip(df['Node'], df['Location']):
    location = location.split(',')
    lat, lon = float(location[0]), float(location[1])
    if node == '':
        folium.CircleMarker(
            location=[lat, lon],radius=1,color="white",fill=True,fill_color="white",fill_opacity=0.1).add_to(initial_map)
    else:
        folium.Marker([lat, lon], popup=f"{node}").add_to(initial_map)

node_cordinate = df['Location'].tolist()
print(df['Node'].tolist()[0])
print(df['Node'].tolist()[-1])
print(";".join(node_cordinate))
new_node_cordinate = []
for location in node_cordinate:
    loc = location.split(",")
    new_node_cordinate.append((float(loc[0]),float(loc[1])))

folium.PolyLine(new_node_cordinate, color="blue", weight=10, opacity=0.7).add_to(initial_map)

initial_map.save("static/map.html")