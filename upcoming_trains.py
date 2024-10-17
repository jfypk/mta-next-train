import requests
import datetime
import pytz
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
# STOP_ID = ["F23N"] #, "D15S" ]# Stop ID for 42nd St Bryant Park
# ROUTE_ID = "F"

def fetch_mta_data(route_id):
    mta_api_url = next((url for key, url in MTA_API_URLS.items() if route_id in key), None)
    if not mta_api_url:
        raise ValueError(f"Invalid route_id: {route_id}")
    response = requests.get(mta_api_url)
    response.raise_for_status()
    return response.content

def log_upcoming_trains(feed_data, route_id, stop_id):
    # Parse the protobuf data
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(feed_data)
    except Exception as e:
        print(f"Error parsing protobuf: {e}")
        return

    current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
    formatted_current_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    print(f"\n")
    print(f"##################################################################")
    print(f"Current time: {formatted_current_time}")
    print(f"##################################################################")
    print(f"\n")
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
    route_id = input("Enter the route ID (e.g., F): ").strip().upper()
    stop_id = input("Enter the stop ID (e.g., F23): ").strip().upper()
    direction = input("Northbound or Southbound? (e.g., N): ").strip().upper()
    
    feed_data = fetch_mta_data(route_id)
    log_upcoming_trains(feed_data, route_id, stop_id + direction)

if __name__ == "__main__":
    main()