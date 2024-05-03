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
    ARENA_CONFIG_KEY = "arena"

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
    WS_LIDAR_ROUTE = GENERAL_WS_CONFIG["lidar_route"]
    WS_LOG_ROUTE = GENERAL_WS_CONFIG["log_route"]
    WS_CAMERA_ROUTE = GENERAL_WS_CONFIG["camera_route"]
    WS_ODOMETER_ROUTE = GENERAL_WS_CONFIG["odometer_route"]
    WS_CMD_ROUTE = GENERAL_WS_CONFIG["cmd_route"]
    WS_PAMI_ROUTE = GENERAL_WS_CONFIG["pami_route"]

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

    # Specific team color
    TEAM = SPECIFIC_CONFIG["team"]

    # Zombie mode
    ZOMBIE_MODE = SPECIFIC_CONFIG["zombie_mode"]
    if "-z" in sys.argv or "--zombie" in sys.argv:
        ZOMBIE_MODE = True
    if "-g" in sys.argv or "--game" in sys.argv:
        ZOMBIE_MODE = False

    # Jack
    JACK_CONFIG = SPECIFIC_CONFIG["jack"]
    JACK_PIN = JACK_CONFIG["pin"]

    # zone_switch
    ZONE_SWITCH_CONFIG = SPECIFIC_CONFIG["zone_switch"]

    # Led strip
    LED_STRIP_CONFIG = SPECIFIC_CONFIG["strip_led"]
    LED_STRIP_PIN = LED_STRIP_CONFIG["pin"]
    LED_STRIP_BRIGHTNESS = LED_STRIP_CONFIG["brightness"]
    LED_STRIP_NUM_LEDS = LED_STRIP_CONFIG["num_leds"]
    LED_STRIP_FREQ = LED_STRIP_CONFIG["frequency"]

    # Rolling Basis
    ROLLING_BASIS_CONFIG = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]
    SPEED_PROFILES = ROLLING_BASIS_CONFIG["go_to_profiles"]["speed"]
    PRECISION_PROFILES = ROLLING_BASIS_CONFIG["go_to_profiles"]["precision"]

    # Actuators
    ACTUATORS_CONFIG = SPECIFIC_CONFIG["actuators"]
    ACTUATOR_TEENSY_SER = ACTUATORS_CONFIG["actuators_teensy_ser"]
    FRONT_GOD_HAND = ACTUATORS_CONFIG["front_god_hand"]
    MINIMUM_DELAY = ACTUATORS_CONFIG["minimum_delay"]

    # Lidar
    LIDAR_CONFIG = SPECIFIC_CONFIG["lidar"]
    LIDAR_ANGLES_UNIT = LIDAR_CONFIG["angles_unit"]
    LIDAR_DISTANCES_UNIT = LIDAR_CONFIG["distances_unit"]
    LIDAR_MIN_ANGLE = LIDAR_CONFIG["min_angle"]
    LIDAR_MAX_ANGLE = LIDAR_CONFIG["max_angle"]
    LIDAR_MIN_DISTANCE_DETECTION = LIDAR_CONFIG["min_distance_detection"]

    # Robot1 brain
    ANTICOLLISION_MODE = SPECIFIC_CONFIG["anticollision_mode"]
    ANTICOLLISION_HANDLE = SPECIFIC_CONFIG["anticollision_handle"]
    STOP_TRESHOLD = SPECIFIC_CONFIG["stop_treshold"]
    MAX_STOP_ANGLE = SPECIFIC_CONFIG["max_stop_angle"]

    # arena
    ARENA_CONFIG = CONFIG_STORE[ARENA_CONFIG_KEY]
