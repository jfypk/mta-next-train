
import xml.etree.ElementTree as ET
import requests
import datetime
import pytz
from fuzzywuzzy import process
from google.transit import gtfs_realtime_pb2

# Constants
MTA_API_URLS = {
    "ACE": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "BDFM": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    "JZ": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "NQRW": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    "1234567": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
}

def find_gtfs_stop_ids(file_path, stop_name):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    stop_info = []
    
    for row in root.findall('.//row'):
        name = row.find('stop_name')
        if name is not None and name.text == stop_name:
            gtfs_stop_id = row.find('gtfs_stop_ids')
            daytime_routes = row.find('daytime_routes')
            if gtfs_stop_id is not None and gtfs_stop_id.text:
                stop_info.append((gtfs_stop_id.text, daytime_routes.text if daytime_routes is not None else "N/A"))
    
    return stop_info

def list_all_stop_names(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    stop_names = set()
    
    for row in root.findall('.//row'):
        stop_name_elem = row.find('stop_name')
        if stop_name_elem is not None and stop_name_elem.text:
            stop_names.add(stop_name_elem.text)
    
    return list(stop_names)

def fuzzy_match_stop_name(query, stop_names, limit=5):
    return process.extract(query, stop_names, limit=limit)

def fetch_mta_data(route_id):
    mta_api_url = next((url for key, url in MTA_API_URLS.items() if route_id in key), None)
    if not mta_api_url:
        raise ValueError(f"Invalid route_id: {route_id}")
    response = requests.get(mta_api_url)
    response.raise_for_status()
    return response.content

def log_upcoming_trains(feed_data, route_id, stop_id):
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(feed_data)
    except Exception as e:
        print(f"Error parsing protobuf: {e}")
        return

    current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
    upcoming_trains = []

    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip_update = entity.trip_update
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == stop_id and trip_update.trip.route_id == route_id:
                    arrival_time = stop_time_update.arrival.time
                    arrival_datetime = datetime.datetime.fromtimestamp(arrival_time, pytz.timezone('US/Eastern'))
                    time_remaining = arrival_datetime - current_time
                    minutes_remaining = int(time_remaining.total_seconds() / 60)
                    upcoming_trains.append((arrival_datetime, minutes_remaining, trip_update.trip.trip_id))

    upcoming_trains.sort(key=lambda x: x[0])

    for arrival_datetime, minutes_remaining, trip_id in upcoming_trains:
        formatted_time = arrival_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')
        print(f"{route_id} Train arriving in {minutes_remaining} minutes at {formatted_time}")

def main():
    file_path = './mta_info.xml'
    try:
        all_stop_names = list_all_stop_names(file_path)
        
        if not all_stop_names:
            print("No stop names found in the XML file.")
            return

        while True:
            user_input = input("\nEnter the name of the stop you want to look up (or 'q' to quit): ")
            if user_input.lower() == 'q':
                break
            
            matches = fuzzy_match_stop_name(user_input, all_stop_names)
            
            print("\nDid you mean one of these stops?")
            for idx, (name, score) in enumerate(matches, start=1):
                print(f"{idx}. {name} (Match score: {score})")
            
            choice = input("\nEnter the number of your choice (or 'n' for a new search): ")
            if choice.lower() == 'n':
                continue
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(matches):
                    selected_stop = matches[index][0]
                    stop_info = find_gtfs_stop_ids(file_path, selected_stop)
                    
                    # THIS ISN"T WORKING PROPERLY
                    if stop_info:
                        print(f"\nGTFS Stop ID(s) and Daytime Routes for {selected_stop}:")
                        for stop_id, routes in stop_info:
                            print(f"Stop ID: {stop_id}, Daytime Routes: {routes}")
                            route_id = input("Enter the route ID (e.g., F): ").strip().upper()
                            direction = input("Northbound or Southbound? (e.g., N): ").strip().upper()
                            feed_data = fetch_mta_data(route_id)
                            log_upcoming_trains(feed_data, route_id, stop_id + direction)
                    else:
                        print(f"\nNo GTFS Stop ID found for {selected_stop}")
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'n' for a new search.")

    except ET.ParseError:
        print(f"Error parsing the XML file: {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
