import os
from dotenv import load_dotenv
import geopandas as gpd
from shapely.geometry import Polygon
from pyproj import Transformer
import os
import requests 
import json
import time
from requests.auth import HTTPBasicAuth

def getPolygons(folderPath):
    """
    Reads all shapefiles in a directory and stores their respective polygons
    in a dictionary
    Params:
        -- folderPath (str, req): Path to folder where shapefiles are stored
    returns:
        -- polygons (dict): Dictionary of polygons indexed by first two letters
                            of site name
    """
    polygons = {}
    for f in os.listdir(folderPath):
        # print(f)
        if f.endswith('.shp'): # only read shapefiles
            fpath = os.path.join(folderPath, f) # get path to shapefile
            gdf = gpd.read_file(fpath) # read shapefile
            for i, geom in enumerate(gdf.geometry):
                if isinstance(geom, Polygon):
                    coords = geom.exterior.coords._coords
                    xy_tuples = []
                    for coord in coords:
                        xy_tuples.append(tuple(coord))
                        
                    if gdf["SITENO"][i] is None:
                        polygons['UVM_gage'] = xy_tuples
                    else:
                        polygons[f'{gdf["SITENO"][i]}'] = xy_tuples
    return polygons


# function definition for searching the stats of each image site 
def search_stats_params(coordinates, StartTime):
    
    return {
    "item_types":[
        "PSScene"
    ],
    "interval": "year",
    "filter":{
        "type":"AndFilter",
        "config":[
            {
                "type":"GeometryFilter",
                "field_name":"geometry",
                "config": {
                    'type':'Polygon',
                    'coordinates':[coordinates]
                }
                        
            },
            {
                "type":"DateRangeFilter",
                "field_name":"acquired",
                "config":{
                "gte":StartTime
                }
            },
            {
                "type":"StringInFilter",
                "field_name":"quality_category",
                "config":[
                "standard"
                ]
            },
            {
                "type":"AssetFilter",
                "config":[
                "ortho_analytic_4b_sr",
                ]
            },
            {
                "type":"RangeFilter",
                "field_name":"cloud_cover",
                "config":{
                "lte":0.50,
                "gte":0.10
                },
            },
            {
                "type":"RangeFilter",
                "field_name":"visible_percent",
                "config":{
                "gte":.95
                },
            },
            {
                "type":"PermissionFilter",
                "config":[
                "assets:download"
                ]
            },
        ]
    }
    }

# function definition to grab the image ids for ordering
def search_params(coordinates, StartTime):
    
    return {
    "item_types":[
        "PSScene"
    ],
    "filter":{
        "type":"AndFilter",
        "config":[
            {
                "type":"GeometryFilter",
                "field_name":"geometry",
                "config": {
                    'type':'Polygon',
                    'coordinates':[coordinates]
                }
                        
            },
            {
                "type":"DateRangeFilter",
                "field_name":"acquired",
                "config":{
                "gte":StartTime
                }
            },
            {
                "type":"StringInFilter",
                "field_name":"quality_category",
                "config":[
                "standard"
                ]
            },
            {
                "type":"AssetFilter",
                "config":[
                "ortho_analytic_4b_sr",
                ]
            },
            {
                "type":"RangeFilter",
                "field_name":"cloud_cover",
                "config":{
                "lte":0.50,
                "gte":0.10
                },
            },
            {
                "type":"RangeFilter",
                "field_name":"visible_percent",
                "config":{
                "gte":.95
                },
            },
            {
                "type":"PermissionFilter",
                "config":[
                "assets:download"
                ]
            },
        ]
    }
    }

def order_params(coordinates, order_name, images):
    return {

    "name": f"{order_name}",
    "source_type": "scenes",
    "products": [
        {
            "item_ids": images,
            "item_type": "PSScene",
            "product_bundle": "analytic_sr_udm2"
        }
    ],
    "tools": [
        {
            "clip": {
                "aoi": {
                    'type': 'Polygon',
                    'coordinates': [coordinates]
                }
            }
        }
    ],
    "order": [
        {
            "name": f"composite-{i}",
            "source_type": "scenes",
            "products": [
                {
                    "item_ids": [images[i]],
                    "item_type": "PSScene",
                    "product_bundle": "ortho_analytic_4b_sr"
                }
            ],
            "tools": [
                {
                    "clip": {
                        "aoi": {
                            'type': 'Polygon',
                            'coordinates': [coordinates]
                        }
                    }
                },
                {
                    "composite": {}
                }
            ]
        }
        for i in range(len(images))
    ],
    "delivery": {
        "single_archive": True,
        "archive_type": "zip",
    }
}

def process_response(data_dict, image_ids):
    if 'features' in data_dict:
        for feature in data_dict['features']:
            image_id = feature['id']
            image_ids.append(image_id)
    else:
        print("No features found in response.")
    return image_ids


def handle_pagination(data_dict, image_ids):
    while '_links' in data_dict and '_next' in data_dict['_links']:
        next_url = data_dict['_links']['_next']
        if not next_url:
            print("No next URL found - stopping")
            break
        retry_attempts = 0
        while True:
            response = requests.get(next_url, headers=headers)
            if response.status_code == 200:
                data_dict = response.json()
                process_response(data_dict, image_ids)
                break
            elif response.status_code == 429:
                retry_attempts += 1
                wait_time = 2 ** retry_attempts
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error: Received status code {response.status_code} while fetching next URL")
                print(response.text)
                response.raise_for_status()
    return image_ids


if __name__ == "__main__":
    # using .env to load in api key
    load_dotenv()
    PLANET_API_KEY = os.getenv('API_KEY')

    # obtaining path to where AOIs are stored, to get polygins
    dir_path = os.getenv('DIR_PATH')
    os.chdir(dir_path)
    polygons = getPolygons(dir_path)

    # making sure connection to planet labs is working
    BASE_URL = 'https://api.planet.com/tasking/v2/orders/'
    auth = HTTPBasicAuth(PLANET_API_KEY, '')
    res = requests.get(url=BASE_URL, auth=auth)
    assert res.status_code == 200

    # setting endpoint and headers for api call 
    SEARCH_ENDPOINT = 'https://api.planet.com/data/v1/stats'
    headers = {
    'Authorization': f'api-key {PLANET_API_KEY}',
    'Content-Type': 'application/json'
    }

    # Create a dictionary to store the total imagery counts and start_time
    START_TIME = '2018-01-01T00:00:00Z'
    count_imagery_dict = {}

    # Loop through keys to search UPS API totals images of each site
    for key, geojson_geometry in polygons.items():
        coordinates = [list(coord) for coord in geojson_geometry]
        search_parameters = search_stats_params(coordinates, START_TIME)

        response = requests.post(SEARCH_ENDPOINT, headers=headers, data=json.dumps(search_parameters))
        data_dict = response.json()  # Directly use response.json() for parsing

        total = sum(bucket['count'] for bucket in data_dict['buckets'])
        count_imagery_dict[key] = total

        print(f'{key} site total images: {total}')
    
    # verifying the images numbers look right 
    user_input = str(input("Do these sites and imagery look right? ENTER (n) to stop and anything else to continue. Enter here: "))
    if user_input.lower() == 'n':
        exit()

    # To grab the image IDs of each site
    SEARCH_ENDPOINT = 'https://api.planet.com/data/v1/quick-search'
    ORDER_ENDPOINT = 'https://api.planet.com/compute/ops/orders/v2'
    image_ids = []
    downloaded = [] 

    # figuring out if user wants a output.txt of 
    write_keys_input = str(input("Would you like a file named 'output.txt' to be written containing all keys"
                                 " that were downloaded? enter (y) to have this done. Enter Here: "))
    keys_output = write_keys_input.lower() == 'y'
    if keys_output:
        f = open("output.txt", "w")

    for curr_key, geojson_geometry in polygons.items():
        if curr_key in downloaded:
            print(f"Already downloaded: {curr_key}")
            continue
        downloaded.append(curr_key)

        # Reset list of images for each new key
        coordinates = [list(coord) for coord in geojson_geometry]
        search_parameters = search_params(coordinates, START_TIME)

        # Request for image IDs
        response = requests.post(SEARCH_ENDPOINT, headers=headers, data=json.dumps(search_parameters))
        data_dict = response.json()  # Use response.json() for better performance
        image_ids = process_response(data_dict, [])
        image_ids = handle_pagination(data_dict, image_ids)
        print(f"Total image IDs retrieved: {len(image_ids)}")
        assert count_imagery_dict[curr_key] == len(image_ids)

        # Sort image IDs
        image_ids.sort()  
        first_image_order, second_image_order = image_ids[:500], image_ids[500:]
        order_name = f'{curr_key}-test-1'

        # making first order
        order_parameters = order_params(coordinates=coordinates, order_name=order_name, images=first_image_order)
        response = requests.post(ORDER_ENDPOINT, headers=headers, data=json.dumps(order_parameters))
        if response.status_code == 202:
             print(f"Request was successful. Currently downloading: {order_name}")
        else:
            print("Request failed.")
            print(response.status_code)
            print(response.text)
            break

        # if necessary make second order
        if len(image_ids) > 500:
            order_name = f'{curr_key}-test-2'
            order_parameters = order_params(coordinates=coordinates, order_name=order_name, images=second_image_order)
            response = requests.post(ORDER_ENDPOINT, headers=headers, data=json.dumps(order_parameters))
            if response.status_code == 202:
                print(f"Request was successful. Currently downloading: {order_name}")
            else:
                print("Request failed.")
                print(response.status_code)
                print(response.text)
                break
        f.write(f"'{curr_key}',")