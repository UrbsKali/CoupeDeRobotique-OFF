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

    # Zombie mode
    ZOMBIE_MODE = SPECIFIC_CONFIG["zombie_mode"]
    if "-z" in sys.argv or "--zombie" in sys.argv:
        ZOMBIE_MODE = True
    if "-g" in sys.argv or "--game" in sys.argv:
        ZOMBIE_MODE = False

    # Jack
    JACK_CONFIG = SPECIFIC_CONFIG["jack"]
    JACK_PIN = JACK_CONFIG["pin"]

    # Team switch
    TEAM_SWITCH_CONFIG = SPECIFIC_CONFIG["team_switch"]
    TEAM_SWITCH_PIN = TEAM_SWITCH_CONFIG["pin"]
    ENABLE_TEAM_SWITCH = TEAM_SWITCH_CONFIG["activated"]
    TEAM_SWITCH_OFF = TEAM_SWITCH_CONFIG["team_off"]
    TEAM_SWITCH_ON = TEAM_SWITCH_CONFIG["team_on"]

    # Led strip
    LED_STRIP_CONFIG = SPECIFIC_CONFIG["strip_led"]

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
    ELEVATOR = ACTUATORS_CONFIG["elevator"]
    SOLAR_PANEL_RIGHT = ACTUATORS_CONFIG["solar_panel"]["right"]

    # Lidar
    LIDAR_CONFIG = SPECIFIC_CONFIG["lidar"]
    LIDAR_ANGLES_UNIT = LIDAR_CONFIG["angles_unit"]
    LIDAR_DISTANCES_UNIT = LIDAR_CONFIG["distances_unit"]
    LIDAR_MIN_ANGLE = LIDAR_CONFIG["min_angle"]
    LIDAR_MAX_ANGLE = LIDAR_CONFIG["max_angle"]
    LIDAR_MIN_DISTANCE_DETECTION = LIDAR_CONFIG["min_distance_detection"]
    LIDAR_FRONTAL_DETECTION_ANGLE = LIDAR_CONFIG["frontal_detection_angle"]
    LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE = LIDAR_CONFIG["semi_circular_detection_angle"]

    # Robot1 brain
    ANTICOLLISION_MODE = SPECIFIC_CONFIG["anticollision_mode"]
    ANTICOLLISION_HANDLE = SPECIFIC_CONFIG["anticollision_handle"]
    STOP_TRESHOLD = SPECIFIC_CONFIG["stop_treshold"]

    # arena
    ARENA_CONFIG = CONFIG_STORE[ARENA_CONFIG_KEY]
