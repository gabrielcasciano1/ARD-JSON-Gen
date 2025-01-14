import json
from datetime import datetime, timedelta
import random
import os

# Creates a directory at the specified location
def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print(f"Directory {dir_name} has been created")
    else:
        print(f"Directory {dir_name} already exists, exitting . . .")
        exit(0)

# Writes a file to the specified filename with the provided data
def write_file(filename, json_data):
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    
    print(json_data)

# Generates a JSON with provided data
def generate_json(filename, area, uid, listLen, dt):
    # Create the JSON structure
    json_data = {
        "Area": area,
        "UID": uid,
        "Datetime": dt,
        "Picklist": random.sample(range(1, listLen + 1), listLen),
        "Picklistlength": listLen
    }
    
    # Write data to file
    write_file(filename, json_data)

# Generates a JSON with the provided data, purposely creates an incorrect list
def generate_json_wrong_list(filename, area, uid, listLen, dt):
    json_data = {
        "Area": area,
        "UID": uid,
        "Datetime": dt,
        "Picklist": random.sample(range(1, listLen + 1), listLen),
        "Picklistlength": random.randint(0, listLen**2)
    }

    write_file(filename, json_data)

if __name__ == "__main__":

    # Get the current time, and use that to create a unique directory name
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    dir_name = f"gen_json_{current_time}"
    make_dir(dir_name) # create the directory

    # Collect paramters from user
    print("Enter the number of JSON to generate.")
    json_count = int(input("The number X entered will geneate X correct, X wrong dates, X wrong UID, X wrong Areas, X wrong picklists: "))
    area_code = int(input("Enter the area number: "))
    uid_start = int(input("Enter the UID start number: "))
    maxListLen = int(input("Enter the max pick list length: "))

    file_count = 1
    uid_count = 0

    # Correct data
    for i in range(0, int(round(json_count, 0))):
        generate_json(f"{dir_name}/json_{file_count:02d}.json", area_code, uid_start + uid_count, random.randint(1, maxListLen), datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        uid_count += 1
        file_count += 1

    # Wrong dates
    for i in range(0, int(round(json_count, 0))):
        date = datetime.now() + timedelta(days=random.randint(-30, 30))
        generate_json(f"{dir_name}/json_{file_count:02d}.json", area_code, uid_start + uid_count, random.randint(1, maxListLen), date.strftime("%Y-%m-%d-%H-%M-%S"))
        uid_count += 1
        file_count += 1

    # Wrong UID
    for i in range(0, int(round(json_count, 0))):
        generate_json(f"{dir_name}/json_{file_count:02d}.json", area_code, random.randint(1, uid_start + uid_count), random.randint(1, maxListLen), datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        uid_count += 1
        file_count += 1

    # Wrong Area
    for i in range(0, int(round(json_count, 0))):
        generate_json(f"{dir_name}/json_{file_count:02d}.json", random.randint(-area_code**2, area_code**2), uid_start + uid_count, random.randint(1, maxListLen), datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        uid_count += 1
        file_count += 1

    # Wrong picklists
    for i in range(0, int(round(json_count, 0))):
        generate_json_wrong_list(f"{dir_name}/json_{file_count:02d}.json", area_code, uid_start + uid_count, random.randint(1, maxListLen), datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        uid_count += 1
        file_count += 1
    
    print("Finished generating files!")
