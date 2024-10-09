import json
from datetime import datetime
import random
import os

def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    else:
        print(f"Directory {dir_name} already exists, exitting . . .")
        exit(0)

def write_file(filename, json_data):
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    
    print(json_data)

def generate_json_correct(filename, area, uid, listLen, dt):
    
    # Create the JSON structure
    json_data = {
        "Area": area,
        "UID": uid,
        "Datetime": dt,
        "Picklist": random.sample(range(1, listLen + 1), listLen),
        "Picklistlength": listLen
    }
    
    write_file(filename, json_data)

def generate_json_wrong(filename, area, uid, listLen, dt):
    json_data = {
        "Area": area + 10,
        "UID": uid,
        "Datetime": dt,
        "Picklist": random.sample(range(1, listLen + 1), listLen),
        "Picklistlength": random.randint(0, len(listLen))
    }

    write_file(filename, json_data)

print("JSON Generator \n")

json_count = int(input("Enter the number of JSON to generate, half will be wrong: "))
json_count = 2 if json_count < 1 else json_count

area_count = int(input("Enter the number of areas: "))
uid_start = int(input("Enter the UID start number: "))
maxListLen = int(input("Enter the max pick list length: "))

current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
dir_name = f"gen_json_{current_time}"
make_dir(dir_name)

file_count = 1
uid_count = 0

for i in range(0, int(round(json_count/2, 0))):
    generate_json_correct(f"{dir_name}/json_{file_count}.json", random.randint(1, area_count), uid_start + uid_count, random.randint(1, maxListLen), datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    uid_count += 1
    file_count += 1


