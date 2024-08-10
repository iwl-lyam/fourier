import json


def read_config():
    try:
        with open("config.json", 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: config.json was not found.")
    except json.JSONDecodeError:
        print(f"Error: config.json is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
