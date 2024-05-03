from config_loader import CONFIG

import math

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from led_strip import LEDStrip
from arena import MarsArena
from GPIO import PIN

# Import from local path
from brains import MainBrain
from controllers import RollingBasis, Actuators
from sensors import Lidar

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # State strip leds
    leds = LEDStrip(
        num_leds=CONFIG.LED_STRIP_NUM_LEDS,
        pin=CONFIG.LED_STRIP_PIN,
        freq=CONFIG.LED_STRIP_FREQ,
        brightness=CONFIG.LED_STRIP_BRIGHTNESS,
    )

    # Loggers
    logger_ws_server = Logger(
        identifier="ws_server",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_brain = Logger(
        identifier="brain",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_rolling_basis = Logger(
        identifier="rolling_basis",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_actuators = Logger(
        identifier="actuators",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_arena = Logger(
        identifier="arena",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_lidar = Logger(
        identifier="lidar",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.CRITICAL,
        file_log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,
    )

    # Routes
    ws_cmd = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_pami = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_log = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Add routes
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    ws_server.add_route_handler(CONFIG.WS_PAMI_ROUTE, ws_pami)
    ws_server.add_route_handler(CONFIG.WS_LOG_ROUTE, ws_log)

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
    jack_pin.setup("input_pulldown", reverse_state=True)

    # Team switch
    team_switch = PIN(CONFIG.TEAM_SWITCH_PIN)
    team_switch.setup("input_pulldown")

    # Robot
    rolling_basis = RollingBasis(logger=logger_rolling_basis)
    rolling_basis.stop_and_clear_queue()
    rolling_basis.set_pid(4.4, 0.0, 0.05)

    # Actuators
    actuators = Actuators(logger=logger_actuators)

    # Arena
    start_zone_id = 0
    arena = MarsArena(
        start_zone_id,
        logger=logger_arena,
        border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
        robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
    )  # must be declared from external calculus interface or switch on the robot

    start_pos = OrientedPoint.from_Point(
        arena.drop_zones[2].zone.centroid,
        3.14 / 2,
    )

    # Set start position
    start_pos = OrientedPoint.from_Point(
        arena.zones["home"].centroid,
        math.pi / 2 if start_zone_id <= 2 else -math.pi / 2,
    )
    rolling_basis.set_odo(start_pos)
    logger_brain.log(f"Start position: {start_pos}", LogLevels.INFO)

    # Brain
    leds.is_ready()
    brain = MainBrain(
        actuators=actuators,
        logger=logger_brain,
        ws_cmd=ws_cmd,
        ws_pami=ws_pami,
        rolling_basis=rolling_basis,
        lidar=lidar,
        arena=arena,
        jack=jack_pin,
        team_switch=team_switch,
        leds=leds,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
