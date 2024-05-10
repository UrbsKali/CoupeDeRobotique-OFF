from config_loader import CONFIG

import math

# Import from common
from logger import Logger, LogLevels
from WS_comms import WServerRouteManager, WSender, WSreceiver, WServer


# Import from local path
from brains import MainBrain
from controllers import Pipou

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # State strip leds
    #leds = LEDStrip(**CONFIG.LED_STRIP_CONFIG)

    # Loggers
    logger_brain = Logger(
        identifier="brain",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_rolling_basis = Logger(
        identifier="Pipou",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_ws_server = Logger(
        identifier="Pipou",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    
    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,
    )
    
    ws_cmd = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)

    # Robot
    pipou = Pipou(logger=logger_rolling_basis)

    # Brain
    #leds.set_is_ready()
    brain = MainBrain(
        logger=logger_brain,
        robot=pipou,
        ws_cmd=ws_cmd
    )
    
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
