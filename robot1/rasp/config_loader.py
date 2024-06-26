import pathlib
import json
import sys
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except Exception:
        raise

    return file_json


class CONFIG:
    # TO CONFIG !
    RELATIVE_ROOT_PATH = os.path.join("..", "..")
    SPECIFIC_CONFIG_KEY = "rob"
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
    GENERAL_TEENSY_CONFIG = GENERAL_CONFIG["teensy"]

    WS_PORT = int(GENERAL_WS_CONFIG["port"])
    WS_CMD_ROUTE = GENERAL_WS_CONFIG["cmd_route"]

    TEENSY_VID = GENERAL_TEENSY_CONFIG["vid"]
    TEENSY_PID = GENERAL_TEENSY_CONFIG["pid"]
    TEENSY_BAUDRATE = GENERAL_TEENSY_CONFIG["baudrate"]
    TEENSY_CRC = GENERAL_TEENSY_CONFIG["crc"]
    TEENSY_DUMMY = GENERAL_TEENSY_CONFIG["dummy"]

    # Specific config
    SPECIFIC_CONFIG = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])

    # Zombie mode
    ZOMBIE_MODE = SPECIFIC_CONFIG["zombie_mode"]
    if "-z" in sys.argv or "--zombie" in sys.argv:
        ZOMBIE_MODE = True
    if "-g" in sys.argv or "--game" in sys.argv:
        ZOMBIE_MODE = False

    # Rolling Basis
    ROLLING_BASIS_CONFIG = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]
