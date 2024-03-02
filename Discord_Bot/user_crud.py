from utility import load_environment_variable
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = load_environment_variable("MONGO_URI")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["outages"]
collection = db['user']

def add_address(user_id, address_name, address, longitude, latitude):
    data = collection.find_one({"user_id": user_id})
    # 确保经度和纬度是浮点数
    longitude = float(longitude)
    latitude = float(latitude)
    # 构建geoJSON格式的位置信息
    location = {
        "type": "Point",
        "coordinates": [longitude, latitude]  # 注意MongoDB中的顺序是 [经度, 纬度]
    }

    if data is None:
        # 执行插入操作
        result = collection.insert_one({
            "user_id": user_id, 
            "addresses": [{
                "name": address_name, 
                "address": address,
                "location": location  # 添加地理位置信息
            }]
        })

        # 获取插入文档的_id
        inserted_id = result.inserted_id

        print(f"Inserted document with _id: {inserted_id}")
        print("User and Address added successfully.")
    else:
        # 使用$push向数组中添加一个新的地址，包含geoJSON位置信息
        result = collection.update_one(
            {"user_id": user_id}, 
            {"$push": {"addresses": {
                "name": address_name, 
                "address": address,
                "location": location  # 添加地理位置信息
            }}}
        )

        # 检查匹配和修改的文档数量
        print(f"Documents matched: {result.matched_count}")
        print(f"Documents modified: {result.modified_count}")

    
def remove_address(user_id, address_name):
    collection.update_one({"user_id": user_id}, {"$pull": {"addresses": {"name": address_name}}} )
def get_addresses(user_id):
    data = collection.find(user_id = id)
    if data is None:
        return None
    else:
        return data['addresses']
