# MTA Train Information System

This directory contains a set of scripts designed to interact with MTA data feeds, parse XML files, and provide real-time train information. The scripts are written in Python and utilize various libraries to fetch, parse, and display data.

DOES NOT SUPPORT STATEN ISLAND RAILWAY

## Files

- **station_parser.py**: This script is responsible for parsing XML files to extract GTFS stop IDs and daytime routes for specified stop names. It provides functionality to list all stop names and retrieve detailed information for a selected stop.

- **upcoming_trains.py**: This script fetches real-time MTA data using the GTFS Realtime API. It logs upcoming train arrival times for a specified route and stop ID, allowing users to see how many minutes remain until the next train arrives.

- **requirements.txt**: Lists all the Python dependencies required to run the scripts in this directory. Ensure you have these installed to avoid any runtime issues.

## Usage

1. **Setup**: 
   - Ensure you have Python installed on your system.
   - Install the required dependencies by running:
     ```
     pip install -r requirements.txt
     ```

2. **Running station_parser.py**:
   - This script requires an XML file (`mta_info.xml`) containing stop information.
   - Execute the script using:
     ```
     python station_parser.py
     ```
   - Follow the on-screen instructions to list stop names and retrieve GTFS stop IDs.

3. **Running upcoming_trains.py**:
   - This script fetches data from the MTA API. Ensure you have internet access.
   - Execute the script using:
     ```
     python upcoming_trains.py
     ```
   - Enter the route ID, stop ID, and direction when prompted to see upcoming train times.

## Notes

- The XML file (`mta_info.xml`) should be structured correctly to ensure the `station_parser.py` script functions as expected.
- The MTA API URL is hardcoded in `upcoming_trains.py`. Ensure it is up-to-date and accessible.
- Error handling is implemented to manage common issues such as file not found, XML parsing errors, and network issues.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
