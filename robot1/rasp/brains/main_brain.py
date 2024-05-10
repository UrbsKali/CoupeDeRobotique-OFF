from brain import Brain
from logger import Logger, LogLevels
from WS_comms import WSclientRouteManager

from controllers import Pipou


class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        robot: Pipou,
        ws_cmd: WSclientRouteManager,
    ) -> None:
        super().__init__(logger, self)
        self.robot = robot
        self.ws_cmd = ws_cmd
        
    from brains.com_brain import zombie_mode
    

            
            
    