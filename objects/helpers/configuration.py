import json
import logging


def read_json_config(file_path):
    try:
        with open(file_path, "r") as file:
            config = json.load(file)  # Load the JSON data into a dictionary
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
        return None


def load_logging_config():
    try:
        with open("logging.json", "r") as file:
            logging_config = json.load(file)
            return logging_config
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
        return None


config = read_json_config("config.json")
project_id = config["project_id"]
