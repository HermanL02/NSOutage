
import aiohttp

async def call_broadcast_api_async(message):
    url = 'http://localhost:8081/broadcast'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'message': message}) as response:
            print("Status:", response.status)
            text = await response.text()
            print("Content:", text)

async def call_send_message_api_async(user_id, message):
    url = 'http://localhost:8081/send-message'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'user_id': user_id, 'message': message}) as response:
            print("Status:", response.status)
            text = await response.text()
            print("Content:", text)
            print(user_id)
async def calculate_polygon_centroid(polygon):
    x_list = [vertex[0] for vertex in polygon]
    y_list = [vertex[1] for vertex in polygon]
    len_polygon = len(polygon)
    x_centroid = sum(x_list) / len_polygon
    y_centroid = sum(y_list) / len_polygon
    return (x_centroid, y_centroid)

async def get_location_name(latitude, longitude):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'format': 'json',
        'lat': latitude,
        'lon': longitude,
        'zoom': 18,  # Adjusting zoom level changes the precision of the query
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                # Try to get detailed information from the address field
                if 'address' in data:
                    address = data['address']
                    # Build the detailed address string
                    # Listed below are some common parts of an address, add or remove as needed
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
            else:
                return "Failed to fetch location details"
async def notify_discord_channel(type, cloud_item):
    # Retreive central point of the geom (if it is a polygon)
    if cloud_item['geom']['type'] == 'Polygon':
        centroid = await calculate_polygon_centroid(cloud_item['geom']['coordinates'][0])
        location_name = await get_location_name(centroid[1], centroid[0])
        location_name += "(Area)"
    elif cloud_item['geom']['type'] == 'Point':
        location_name = await get_location_name(cloud_item['geom']['coordinates'][1], cloud_item['geom']['coordinates'][0])
    
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

    await call_broadcast_api_async(message)
async def notify_discord_user(type, users, cloud_item):
    # Retreive central point of the geom (if it is a polygon)
    if cloud_item['geom']['type'] == 'Polygon':
        centroid = await calculate_polygon_centroid(cloud_item['geom']['coordinates'][0])
        location_name = await get_location_name(centroid[1], centroid[0])
        location_name += "(Area)"
    elif cloud_item['geom']['type'] == 'Point':
        location_name = await get_location_name(cloud_item['geom']['coordinates'][1], cloud_item['geom']['coordinates'][0])
    message = f""" {type} Outage: 
    This is related to one of your subscribed locations.
        {cloud_item['title']}
        "Location": {location_name},
        "cause": {cloud_item['cause']},
        "cluster": {cloud_item['cluster']},
        "Influenced People": {cloud_item['val']},
        "Started at": {cloud_item['start']},
        "Previous Estimated End Time": {cloud_item['etr']}
        For official information visit: https://outagemap.nspower.ca/external/default.html
        """
    for i in users:
        print(i)
        await call_send_message_api_async(i, message)