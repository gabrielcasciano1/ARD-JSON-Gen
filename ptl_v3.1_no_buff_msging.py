import os
import json
import glob
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from pycomm3 import LogixDriver
JSON_DIRECTORY = 'C:\\Users\\Daniil Bryzgalov\\Desktop\\IIoT_PickToLight\\JSON_registry'
DB_PATH = 'uid_registry.db'
UID_FILE = 'UID_registry.txt'
LOCATION_LIMITS = (1, 5)
AREA = 6
PLC_IP = '127.0.0.1'

class UIDRegistry(ABC):
    @abstractmethod
    def __init__(self, path: str):
         pass
    @abstractmethod
    def save_processed_uids(self, uids_to_save: set[int]) -> None:
        pass

    @abstractmethod
    def load_processed_uids(self) -> set[int]:
        pass
    
    @abstractmethod
    def get_highest_uid(self) -> int:
        pass
    
    @abstractmethod
    def exists(self, uid: int) -> bool:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass

class TextFileUIDRegistry(UIDRegistry):
    "File-based UID storage class"
    def __init__(self, file_path: str):
        self.registry_path = file_path
        # Ensure the file exists before starting
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, 'w') as file:
                pass  # Create an empty file if it doesn't exist
    
    def save_processed_uids(self, uids_to_save: set[int]) -> None: # Append new UIDs to the text file (not rewriting the file every time for efficiency)
        with open(self.registry_path, 'a') as file:
            for uid in uids_to_save:
                file.write(f"{uid}\n")
     
    def load_processed_uids(self) -> set[int]: # Load processed UIDs from a file and return them as a set.
        try:
            with open(self.registry_path, 'r') as file:
                # Read all UIDs from the file, stripping newline characters
                return set(int(line.strip()) for line in file.readlines() if line.strip().isdigit())
        except FileNotFoundError:
            # If the file doesn't exist yet, return an empty set
            return set()
    
    def get_highest_uid(self) -> int: # Retrieve the highest UID from the file
        with open(self.file_path, 'r') as file:
            uids = [int(line.strip()) for line in file if line.strip().isdigit()]
        return max(uids) if uids else 0  # Return 0 if no UIDs exist

    def exists(self, uid: int) -> bool:
        uid_str = str(uid)  # Convert UID to string for comparison
        with open(self.file_path, 'r') as file:
            return any(line.strip() == uid_str for line in file)
    
    def close(self):
        pass

class SQLiteUIDRegistry(UIDRegistry): # Database handler
    "SQLite-based UID storage class"
    '''__instance = None
    
    def __new__(cls, *args, **kwagrs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        
        return cls.__instance'''

    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        cursor = self.connection.cursor()
    
        # Create a table for storing processed UIDs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS uid_registry (
            uid INTEGER PRIMARY KEY
        )
        ''')
        cursor.close()
        self.connection.commit()

    
    def save_processed_uids(self, uids_to_save: set[int]) -> None: # Bulk save processed UIDs into the SQLite database after processing all files
        cursor = self.connection.cursor()
        cursor.executemany('INSERT OR IGNORE INTO uid_registry (uid) VALUES (?)', [(uid,) for uid in uids_to_save])
        cursor.close()
        self.connection.commit()
    
    def load_processed_uids(self) -> set[int]: # Load processed UIDs from the SQLite database
        cursor = self.connection.cursor()
        cursor.execute('SELECT uid FROM uid_registry')
        uids = cursor.fetchall()
        cursor.close()
        return set(int(uid[0]) for uid in uids)
    
    def get_highest_uid(self) -> int: # Retrieve the highest UID from the SQLite database
        cursor = self.connection.cursor()
        cursor.execute('SELECT MAX(uid) FROM uid_registry')
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result[0] else 0  # Return 0 if no UIDs exist
    
    def exists(self, uid: int) -> bool: #Check if a given UID exists in the database.
        cursor = self.connection.cursor()
        cursor.execute('SELECT 1 FROM uid_registry WHERE uid = ?', (uid,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
        
    def close(self) -> None:
        self.connection.close()

"""def monitor_tags(plc, pick_list, all_picked_event):
    "Function to monitor tags and signal when all are False."

    while not all_picked_event.is_set(): # Wait until all tags are False (i.e All items picked and buttons pressed)
        # Check all tags and filter those still True
        locations_to_pick = list(
            location for location in pick_list
            if plc.read(f"_IO_EM_DO_0{location-1}").value
        )
        if not locations_to_pick:  # All tags are False
            all_picked_event.set()  # Signal completion
            return

def print_status(plc, pick_list, all_picked_event):
    "Function to print the status of the tags periodically."
    while not all_picked_event.is_set():
        locations_to_pick = list(
            location for location in pick_list
            if plc.read(f"_IO_EM_DO_0{location-1}").value
        )
        # Print a message every 10 seconds
        print(f"Locations left to pick: {locations_to_pick}")
        time.sleep(10)"""

def io_controller(pick_list: str):
    try:
        with LogixDriver(PLC_IP, init_tags=True, init_program_tags=False) as plc:
            # Write True to all corresponding tags for the pick list (i.e. turn ON the lights in all locations)
            for location in pick_list:
                tag_name = f"_IO_EM_DO_0{location-1}"
                plc.write(tag_name, True)
            
            last_message_time = time.time()
            while True:
                # Check all tags and filter those still True
                locations_to_pick = list(
                    location for location in pick_list
                    if plc.read(f"_IO_EM_DO_0{location-1}").value
                )

                if not locations_to_pick:  # Exit loop immediately if all buttons are pressed
                    print("All items picked successfully!")
                    break

                # Print a message every 10 seconds
                current_time = time.time()
                if current_time - last_message_time >= 10:
                    print(f"Locations left to pick: {locations_to_pick}")
                    last_message_time = current_time

                # Small sleep to avoid tight polling loop
                time.sleep(0.1)
            """
            # Event to synchronize threads
            all_picked_event = threading.Event()

            # Start the monitoring thread
            monitor_thread = threading.Thread(target=monitor_tags, args=(plc, pick_list, all_picked_event))
            monitor_thread.start()

            # Start the printing thread
            print_thread = threading.Thread(target=print_status, args=(plc, pick_list, all_picked_event))
            print_thread.start()

            # Wait for the monitoring thread to signal completion
            all_picked_event.wait()

            print("All items picked successfully!")

            # Ensure both threads have finished
            monitor_thread.join()
            print_thread.join()"""

    except Exception as e:
        print(f"Error during PLC communication: {e}")

def validate_area(area: int) -> None:
    if area != AREA:
        raise ValueError("Pick list is for a different area or the area is invalid")

def validate_length(length: int, pick_list: set[int]) -> None:
    # Validate length data field consistency 
    if len(pick_list) != length: 
        raise ListLengthError()

    # Check if the pick list length is not zero
    if len(pick_list) == 0:
        raise ListLengthError("Pick list is empty.")

def validate_locations(pick_list: set[int]) -> None: # Check that Bin Locations are valid
    for locations in pick_list:
        if int(locations) > LOCATION_LIMITS[1] or int(locations) < LOCATION_LIMITS[0]:
            raise PickLocationError

def validate_date(date_str: str) -> None:
    # Define the format for parsing the date string
    date_format = "%Y-%m-%d-%H-%M-%S"

    # Parse the date string into a datetime object
    try:
        input_date = datetime.strptime(date_str, date_format)
    except ValueError:
        raise ValueError("Input date is invalid. The correct format 'YYYY-MM-DD-HH-MM-SS'")
    # Get the current time
    now = datetime.now()
    if input_date > now:
        raise DateError("Pick List creation date is in the future.")
    # Check if the input date is less than 24 hours old
    if now - input_date >= timedelta(days=1):
        raise DateError("Pick List creation date is older than 24 hours.")

def validate_JSON(length: int, pick_list: set[int], list_date: str, area_code: int) -> None:
    # Validate the length of the pick list
    validate_length(length, pick_list)
    
    # Check if the input date is not in the future and less than 24 hours old
    validate_date(list_date)

    # Check that Bin Locations are valid
    validate_locations(pick_list)

    #Check that the pick list is intended for the correct area
    validate_area(area_code)

def unpack_JSON(path: str, processed_UIDs: set[int], highest_uid: int):
        pick_list = list()
        try:
            with open(path, 'r') as listJSON:
                data = json.load(listJSON)
                current_uid = int(data["UID"])

                # Check if the UID has the new highest value, otherwise check if the UID has already been processed
                if current_uid <= highest_uid and current_uid in processed_UIDs:
                    raise ValueError(f"UID {data['UID']} has already been processed.")  # Skip processing for this UID

                validate_JSON(int(data["Picklistlength"]), data["Picklist"], data["Datetime"], data["Area"])
                
                # Add pick locations to the list
                pick_list = data["Picklist"]

                if current_uid > highest_uid:
                    highest_uid = current_uid  # Update the highest UID dynamically
                
                return pick_list, current_uid, highest_uid
                                   
        except (ListLengthError, DateError, PickLocationError, ValueError) as e:
                print(f'{e}')
        except FileNotFoundError:
              print('Specified Pick List does not exist')
        except Exception as e:
                print(f'Unexpected Error ocurred: {e}')    
        return None, None, highest_uid

class ListLengthError(Exception):
        def __init__(self, message = "'Picklistlength' value is different from the actual Pick List length"):
                super().__init__(message)
class DateError(Exception):
       def __init__(self, message="Pick List creation date is older than 24 hours."):
                super().__init__(message)
class PickLocationError(ValueError):
       def __init__(self, message="Pick Location Value is out of bounds"):
                super().__init__(message)

# Driver Code
if __name__ == "__main__":
    uid_registry = SQLiteUIDRegistry(DB_PATH) # Initialize the database and start processing JSON files
    processed_UIDs = uid_registry.load_processed_uids()
    highest_uid = int(uid_registry.get_highest_uid()) # Initialize with the highest UID from the database
    uids_to_save = set()  # To store UIDs for batch saving after all files are processed
    print(f"All processed ids: {processed_UIDs}")
    print(f"New processed ids: {uids_to_save}")
    print(f"Highest id: {highest_uid}")
    json_files = glob.glob(os.path.join(JSON_DIRECTORY, "*.json")) 
    for json_file in json_files:
            pick_list, new_uid, highest_uid = unpack_JSON(json_file, processed_UIDs, highest_uid)
            if pick_list:
                print(f"{pick_list} for {os.path.basename(json_file)}")
                io_controller(pick_list)
            else:
                print(f"No new data processed for {os.path.basename(json_file)}")
            
            # if new uid is a valid one
            if new_uid:
                # Add the newly processed UID to the set for batch insertion   
                uids_to_save.add(new_uid)
                # Update processed UIDs in local memory
                processed_UIDs.add(new_uid)
            
            input("Press Enter to continue...")  # Wait for user input

    # Save all new UIDs to the database after processing all JSON files
    uid_registry.save_processed_uids(uids_to_save)
    print(f"All processed ids: {processed_UIDs}")
    print(f"New processed ids: {uids_to_save}")
    print(f"Highest id: {highest_uid}") 
    # Close the SQLite connection when done
    uid_registry.close()

#TODO: for program run highest_uid is actually highest valid uid
#TODO: Solve problems with threading
#TODO: Write tests
#TODO: caching
#TODO: search implementation in class. self.processed uid where it stores pointer to the table in SQL and a local variable in file?
#TODO: logging in case connection drops
#TODO: wait in case connection unsuccessful
#TODO: Prevent default constructor from executing -> static variable (signleton) + the singleton check in every method for db/file existance
#TODO: Shortest path