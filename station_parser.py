import xml.etree.ElementTree as ET

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

def main():
    file_path = './mta_info.xml'
    try:
        all_stop_names = list_all_stop_names(file_path)
        
        if not all_stop_names:
            print("No stop names found in the XML file.")
            return

        print("Available Stops:")
        for index, name in enumerate(all_stop_names, start=1):
            print(f"{index}. {name}")
        
        while True:
            try:
                user_input = input("\nEnter the index number of the stop you want to look up (or 'q' to quit): ")
                if user_input.lower() == 'q':
                    break
                
                index = int(user_input) - 1
                if 0 <= index < len(all_stop_names):
                    selected_stop = all_stop_names[index]
                    stop_info = find_gtfs_stop_ids(file_path, selected_stop)
                    
                    if stop_info:
                        print(f"\nGTFS Stop ID(s) and Daytime Routes for {selected_stop}:")
                        for stop_id, routes in stop_info:
                            print(f"Stop ID: {stop_id}, Daytime Routes: {routes}")
                    else:
                        print(f"\nNo GTFS Stop ID found for {selected_stop}")
                else:
                    print("Invalid index number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")

    except ET.ParseError:
        print(f"Error parsing the XML file: {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()