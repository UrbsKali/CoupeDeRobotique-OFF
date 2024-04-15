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
    SPECIFIC_CONFIG_KEY = "robot1"
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
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_SERVER_IP = SPECIFIC_WS_CONFIG["server_ip"]

    # Rolling Basis
    ROLLING_BASIS_CONFIG = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]

    # Actuators
    ACTUATORS_CONFIG = SPECIFIC_CONFIG["actuators"]
    ACTUATOR_TEENSY_SER = ACTUATORS_CONFIG["actuators_teensy_ser"]
    GOD_HAND_GRAB_SERVO_PINS_LEFT = ACTUATORS_CONFIG["god_hand_grab_servo_pins_left"]
    GOD_HAND_GRAB_SERVO_PINS_RIGHT = ACTUATORS_CONFIG["god_hand_grab_servo_pins_right"]
    GOD_HAND_DEPLOYMENT_SERVO_PIN = ACTUATORS_CONFIG["god_hand_deployment_servo_pin"]
    GOD_HAND_GRAB_SERVO_OPEN_ANGLE = ACTUATORS_CONFIG["god_hand_grab_servo_open_angle"]
    GOD_HAND_DEPLOYMENT_SERVO_DEPLOY_ANGLE = ACTUATORS_CONFIG[
        "god_hand_deployment_servo_deploye_angle"
    ]
    GOD_HAND_DEPLOYMENT_SERVO_UNDEPLOY_ANGLE = ACTUATORS_CONFIG[
        "god_hand_deployment_servo_undeploy_angle"
    ]
    GOD_HAND_GRAB_SERVO_CLOSE_ANGLE_DIFF_LEFT = ACTUATORS_CONFIG[
        "god_hand_grab_servo_close_angle_diff_left"
    ]
    GOD_HAND_GRAB_SERVO_CLOSE_ANGLE_DIFF_RIGHT = ACTUATORS_CONFIG[
        "god_hand_grab_servo_close_angle_diff_right"
    ]

    # Lidar
    LIDAR_CONFIG = SPECIFIC_CONFIG["lidar"]
    LIDAR_ANGLES_UNIT = LIDAR_CONFIG["angles_unit"]
    LIDAR_DISTANCES_UNIT = LIDAR_CONFIG["distances_unit"]
    LIDAR_MIN_ANGLE = LIDAR_CONFIG["min_angle"]
    LIDAR_MAX_ANGLE = LIDAR_CONFIG["max_angle"]
    LIDAR_MIN_DISTANCE_DETECTION = LIDAR_CONFIG["min_distance_detection"]
