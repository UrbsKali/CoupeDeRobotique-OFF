from config_loader import CONFIG

# Import from common
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from GPIO import PIN

# Import from local path
from brains import MainBrain
from controllers import RollingBasis, Actuators
from sensors import Lidar
import math

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Loggers
    logger_ws_client = Logger(
        identifier="ws_client",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.CRITICAL,
        file_log_level=LogLevels.DEBUG,
    )
    logger_brain = Logger(
        identifier="brain",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_rolling_basis = Logger(
        identifier="rolling_basis",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_actuators = Logger(
        identifier="actuators",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_arena = Logger(
        identifier="arena",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_lidar = Logger(
        identifier="lidar",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.FATAL,
        file_log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_client = WSclient(
        logger=logger_ws_client, host=CONFIG.WS_SERVER_IP, port=CONFIG.WS_PORT
    )
    # Routes
    ws_cmd = WSclientRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_pami = WSclientRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    # Sensors
    ws_lidar = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_odometer = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_camera = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    # Add routes
    ws_client.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    ws_client.add_route_handler(CONFIG.WS_PAMI_ROUTE, ws_pami)
    ws_client.add_route_handler(CONFIG.WS_LIDAR_ROUTE, ws_lidar)
    ws_client.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, ws_odometer)
    ws_client.add_route_handler(CONFIG.WS_CAMERA_ROUTE, ws_camera)

    # Lidar
    lidar = Lidar(
        logger=logger_lidar,
        min_angle=CONFIG.LIDAR_MIN_ANGLE,
        max_angle=CONFIG.LIDAR_MAX_ANGLE,
        unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
        unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
        min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
    )

    # Jack
    jack_pin = PIN(CONFIG.JACK_PIN)
    jack_pin.setup("input_pulldown")

    # Robot
    rolling_basis = RollingBasis(logger=logger_rolling_basis)
    actuators = Actuators(logger=logger_actuators)

    # Arena
    start_zone_id = 0
    arena = MarsArena(
        start_zone_id, logger=logger_arena
    )  # must be declared from external calculus interface or switch on the robot

    start_pos = OrientedPoint.from_Point(
        arena.zones["home"].centroid,
        math.pi / 2 if start_zone_id <= 2 else -math.pi / 2,
    )

    rolling_basis.set_odo(start_pos)
    logger_brain.log(f"Start position: {start_pos}", LogLevels.INFO)

    # Brain
    brain = MainBrain(
        actuators=actuators,
        logger=logger_brain,
        ws_cmd=ws_cmd,
        ws_lidar=ws_lidar,
        ws_odometer=ws_odometer,
        ws_camera=ws_camera,
        rolling_basis=rolling_basis,
        lidar=lidar,
        arena=arena,
        jack=jack_pin,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_client.add_background_task(routine)

    ws_client.run()
