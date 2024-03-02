import os
from dotenv import load_dotenv
import requests
import json
def load_environment_variable(var_name):
    var_value = os.getenv(var_name)
    if var_value is None:
        load_dotenv()  
        var_value = os.getenv(var_name)
    return var_value

def call_broadcast_api_sync(message):
    url = 'http://localhost:8081/broadcast'  
    response = requests.post(url, json={'message': message})
    print("Status:", response.status_code)
    print("Content:", response.text)
def calculate_polygon_centroid(polygon):
    x_list = [vertex[0] for vertex in polygon]
    y_list = [vertex[1] for vertex in polygon]
    len_polygon = len(polygon)
    x_centroid = sum(x_list) / len_polygon
    y_centroid = sum(y_list) / len_polygon
    return (x_centroid, y_centroid)

def get_location_name(latitude, longitude):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'format': 'json',
        'lat': latitude,
        'lon': longitude,
        'zoom': 18,  # 调整zoom级别可以改变查询的精度
    }
    response = requests.get(url, params=params)
    data = response.json()
    # 尝试从address字段获取详细信息
    if 'address' in data:
        address = data['address']
        # 构建具体的地址字符串
        # 下面列出的是一些常见的地址组成部分，你可以根据需要添加或删除
        parts = [
            address.get('road'),
            address.get('suburb'),
            address.get('city_district'),
            address.get('city'),
            address.get('county'),
            address.get('state'),
            address.get('postcode'),
            address.get('country'),
        ]
        detailed_address = ', '.join([part for part in parts if part is not None])
        return detailed_address if detailed_address else data.get('display_name', "Location name not found")
    else:
        return "Location name not found"
def notify_discord(type, cloud_item):
    # Retreive central point of the geom (if it is a polygon)
    if cloud_item['geom']['type'] == 'Polygon':
        centroid = calculate_polygon_centroid(cloud_item['geom']['coordinates'][0])
        location_name = get_location_name(centroid[1], centroid[0])
        location_name += "(Area)"
    elif cloud_item['geom']['type'] == 'Point':
        location_name = get_location_name(cloud_item['geom']['coordinates'][1], cloud_item['geom']['coordinates'][0])
    
    message = f""" {type} Outage: 
        {cloud_item['title']}
        "Location": {location_name},
        "cause": {cloud_item['cause']},
        "cluster": {cloud_item['cluster']},
        "Influenced People": {cloud_item['val']},
        "Started at": {cloud_item['start']},
        "Previous Estimated End Time": {cloud_item['etr']}
        For official information visit: https://outagemap.nspower.ca/external/default.html
        """

    call_broadcast_api_sync(message)
