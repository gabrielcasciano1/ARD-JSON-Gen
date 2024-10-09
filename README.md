# READ ME

## JSON Generator Application

Use this application to generate JSON files. Useage should be self explanitory as the application requests the information it requires in-order to generate a pick list. 

The application creates multiple JSON files and inserts them into a directpry that it creates. The directory has the current datetime embedded in the directories name, an example directory would be 'gen_json_2024-10-09-12-54-18', the date format is 'YYYY-MM-DD-HH-MM-SS'. 

The generator will create 1 correct and 4 incorrect JSON for each X pick-lists requested, the 4 incorrect will have one of the following properties:
- Incorrect Date
- Incorrect UID
- Incorrect Area code
- Incorrect Picklist length