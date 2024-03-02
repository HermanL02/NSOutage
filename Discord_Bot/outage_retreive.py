
import requests
import json
import polyline
from pymongo import MongoClient
from requests.exceptions import ConnectTimeout, ConnectionError
from urllib3.exceptions import MaxRetryError
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from libs.common import load_environment_variable
from notification import notify_discord_channel
from notification import notify_discord_user
import asyncio

ip = load_environment_variable("IP_ADDRESS")
token = load_environment_variable("DISCORD_BOT_TOKEN")
uri = load_environment_variable("MONGO_URI")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["outages"]
collection = db['outages']
usersCollection = db['user']

# Retreive the latest data from the server
def retreive_latest_data(ip):
    try:
        # request from ip
        api = "http://"+ ip + ":8080/data"
        # request with max wait time 15 seconds
        response = requests.get(api, timeout=600)
        # return the json data
        return response.json()
    except ConnectTimeout:
        print("Connection to the server timed out.")
    except ConnectionError:
        print("Failed to establish a connection to the server.")
    except MaxRetryError:
        print("Max retries exceeded with the server.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def decode_json(json_data):
    # decode the json data
    id = json_data.get("id", "No Information")
    title = json_data.get("title", "No Information")
    desc = json_data.get("desc", {})

    cause = desc.get("cause", "No Information")
    cluster = desc.get("cluster", "No Information")

    cust_a = desc.get("cust_a", {})
    val = cust_a.get("val", "No Information")

    start = desc.get("start", "No Information")
    etr = desc.get("etr", "No Information")
    geom = json_data.get("geom", "No Information")
    
    decoded_values = []

    for sublist in geom.values():
        for value in sublist:
            decoded = polyline.decode(value)
            decoded_values.append(decoded)
    mongo_title = title
    mongo_geom = [coordinates_to_geojson(coords) for coords in decoded_values]
    mongo_cause = cause
    mongo_cluster = cluster
    mongo_val = val
    mongo_start = start
    mongo_etr = etr
    mongo_jsons = []
    for i in mongo_geom:
        mongo_json = {
            "title": mongo_title,
            "geom": i,
            "cause": mongo_cause,
            "cluster": mongo_cluster,
            "val": mongo_val,
            "start": mongo_start,
            "etr": mongo_etr
        }
        mongo_jsons.append(mongo_json)
    return mongo_jsons

def coordinates_to_geojson(coords):
    if len(coords) == 1:
        return {
            "type": "Point",
            "coordinates": coords[0][::-1]
        }
    else:
        new_coordinates = []  # 新坐标列表
        for poly in coords:  # 遍历每个多边形
            new_coordinates.append((poly[1],poly[0]))  # 将转换后的多边形坐标添加到列表中
        return {
            "type": "Polygon",
            "coordinates": [new_coordinates]
        }

async def send_notify_user_request(type,localitem):
    geoJson = localitem['geom']
    if geoJson["type"] == "Point":
        # search the subscription
        # GeoJSON点

        # 执行查询
        query_result = usersCollection.find({
        "addresses.location": {
            "$near": {
            "$geometry": geoJson,
            "$maxDistance": 50
            }
        }
        })
        user_ids = [doc["user_id"] for doc in query_result if "user_id" in doc]
    elif geoJson["type"] == "Polygon":
        # search the subscription
        # GeoJSON多边形


        # 执行查询
        query_result = usersCollection.find({
        "addresses.location": {
            "$geoWithin": {
            "$geometry": geoJson
            }
        }
        })
        user_ids = [doc["user_id"] for doc in query_result if "user_id" in doc]
    await notify_discord_user(type,user_ids,localitem)
    print("Notified users:", user_ids)
async def update_into_mongo(mongo_json):
    # Fields to compare
    fields_to_compare = ['title', 'cause', 'cluster', 'val', 'start', 'etr']
    # Assuming the rest of your function is correct
    cloud_items = collection.find({})
    # Serialize each geom list to a JSON string for use as hashable keys
    cloud_geoms = {json.dumps(item['geom'], sort_keys=True): item for item in cloud_items}

    for local_item in mongo_json:
        # Serialize the local geom list to a JSON string
        local_geom_serialized = json.dumps(local_item['geom'], sort_keys=True)
        if local_geom_serialized not in cloud_geoms:
            # If the serialized geom is not in cloud_geoms, insert the item
            collection.insert_one(local_item)
            print("Inserted item with geom:", local_item['geom'])
            await notify_discord_channel("New", local_item)
            await send_notify_user_request("New",local_item)
        else:
            # If it exists, proceed with your comparison and update logic
            cloud_item = cloud_geoms[local_geom_serialized]
            # Your existing logic for comparison and updating
            differences = compare_items(local_item, cloud_item, fields_to_compare)
            if differences:
                # Update cloud data if inconsistent
                update_fields = {field: local_item[field] for field in differences}
                collection.update_one({'_id': cloud_item['_id']}, {'$set': update_fields})
                print(f"Updated item with geom: {local_item['geom']}. Fields updated: {', '.join(differences)}")
                await notify_discord_channel(f"Updated {differences}", local_item)
                await send_notify_user_request(f"Updated {differences}", local_item)
            else:
                print(f"Item with geom: {local_item['geom']} is already up to date.")

async def delete_from_mongo(local_json):
    # 序列化本地 geom 列表
    local_geoms = set(json.dumps(item['geom'], sort_keys=True) for item in local_json)

    # 遍历云端数据
    cloud_items = collection.find({})
    for cloud_item in cloud_items:
        # 类似地，序列化云端 geom 列表
        cloud_geom_serialized = json.dumps(cloud_item['geom'], sort_keys=True)
        # 检查这个序列化的 geom 是否存在于本地数据中
        if cloud_geom_serialized not in local_geoms:
            # 如果云端有而本地没有，则删除
            collection.delete_one({'_id': cloud_item['_id']})
            await notify_discord_channel("Resolved", cloud_item)
            await send_notify_user_request("Resolved", cloud_item)
            




def compare_items(local_item, cloud_item, fields_to_compare):
    # 这个函数需要定义，用于比较本地项目和云端项目的字段差异
    # 返回字段名称列表，这些字段在两个项目之间有差异
    differences = []
    for field in fields_to_compare:
        if local_item.get(field) != cloud_item.get(field):
            differences.append(field)
    return differences

async def main():
    try: 
        jsons = retreive_latest_data(ip)
        d_list = []
        for i in jsons:      
            decoded = decode_json(i)
            for j in decoded:
                d_list.append(j)
        print(len(d_list))
        await update_into_mongo(d_list)
        await delete_from_mongo(d_list)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def loop_main_forever(interval):
    while True:
        await main()
        await asyncio.sleep(interval)  # 等待interval秒，这里设置为120秒

if __name__ == '__main__':
    interval = 120  # 每2分钟运行一次
    asyncio.run(loop_main_forever(interval))

    