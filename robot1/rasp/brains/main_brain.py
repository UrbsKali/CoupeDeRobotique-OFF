from brain import Brain
from logger import Logger, LogLevels
from WS_comms import WSclientRouteManager

from controllers import Pipou

import asyncio

# Import from common
from config_loader import CONFIG

from brain import Brain

from WS_comms import WSmsg, WServerRouteManager
from logger import Logger, LogLevels

class MainBrain(Brain):
    def __init__(
        self,
        logger: Logger,
        robot: Pipou,
        ws_cmd: WSclientRouteManager
    ) -> None:
        super().__init__(logger, self)
        self.robot = robot
        self.ws_cmd = ws_cmd
    
    @Brain.task(process=False, run_on_start=True, refresh_rate=0.01)
    async def zombie_mode(self):
        """
        executes requests received by the server. Use Postman to send request to the server
        Use eval and await eval to run the code you want. Code must be sent as a string
        """
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(
                f"Zombie instruction {cmd.msg} received: {cmd.data}",
                LogLevels.INFO,
            )

            if cmd.msg == "eval":
                instructions = []
                if isinstance(cmd.data, str):
                    instructions.append(cmd.data)
                elif isinstance(cmd.data, list):
                    instructions = cmd.data

                for instruction in instructions:
                    if instruction.startswith("await "):
                        await eval(instruction.removeprefix("await "))
                    else:
                        eval(instruction)

            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )

                
                
        