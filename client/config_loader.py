import numpy as np
import pathlib
import json
import sys
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except Exception as error:
        print(f"Error while loading the file {file_path}: {error}")
        raise error

    return file_json


def format_path(path: str) -> str:
    """
    Transform a path with this shape: '.|folder|sub_folder|file.txt'
    to the path with the correct separator  ('\' for Windows or '/' for Unix-based systems),
    depending on the operating system.
    """
    try:
        path_parts = path.split("|")
        return os.path.join(*path_parts)
    except Exception as error:
        print(f"Error while formatting the path {path}: {error}")
        raise error


class CONFIG:
    # TO CONFIG !
    RELATIVE_ROOT_PATH = os.path.join("..")
    SPECIFIC_CONFIG_KEY = "computer"
    GENERAL_CONFIG_KEY = "general"

    # Directory path (dont't touch)
    ROOT_DIR = os.path.abspath(RELATIVE_ROOT_PATH)
    BASE_DIR = pathlib.Path(__file__).resolve().parent
    COMMON_DIR = os.path.join(ROOT_DIR, "common")
    sys.path.append(
        COMMON_DIR
    )  # Add common directory to the path (to be able to import common modules)
    CONFIG_STORE = load_json_file(os.path.join(ROOT_DIR, "config.json"))

    # CONSTANTS TO DEFINE !
    # General config
    GENERAL_CONFIG = CONFIG_STORE[GENERAL_CONFIG_KEY]
    GENERAL_WS_CONFIG = GENERAL_CONFIG["ws"]

    WS_PORT = int(GENERAL_WS_CONFIG["port"])
    WS_CMD_ROUTE = GENERAL_WS_CONFIG["cmd_route"]

    # Specific config
    SPECIFIC_CONFIG = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])
