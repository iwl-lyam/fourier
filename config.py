"""Initialises configuration file for Fourier"""

import json


def read_config():
    """Does the thing"""
    try:
        with open("config.json", 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Error: config.json was not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: config.json is not a valid JSON file.")
        return {}
