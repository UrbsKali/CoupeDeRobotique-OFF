# External imports
# ..

# Import from common
from config_loader import CONFIG
import asyncio
from brain import Brain

from WS_comms import WSmsg, WServerRouteManager
from geometry import OrientedPoint, Point
from logger import Logger, LogLevels

# Import from local path
# from sensors import Lidar


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def camera_com(self):
    """
    Get camera information: ArUcO and Green Objects (plants) positions
    """
    msg = await self.ws_camera.receiver.get()
    if msg != WSmsg():
        if msg.msg == "arucos":
            self.arucos = msg.data
        elif msg.msg == "green_objects":
            self.green_objects == msg.data


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def odometer_com(self):
    """
    Send ROB current odometer to server
    """
    if self.rolling_basis.odometrie is not None:
        await self.ws_odometer.sender.send(
            WSmsg(
                msg="odometer",
                data=[
                    self.rolling_basis.odometrie.x,
                    self.rolling_basis.odometrie.y,
                    self.rolling_basis.odometrie.theta,
                ],
            )
        )


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
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
                eval(instruction)

        elif cmd.msg == "await_eval":

            instructions = []
            if isinstance(cmd.data, str):
                instructions.append(cmd.data)
            elif isinstance(cmd.data, list):
                instructions = cmd.data

            for instruction in instructions:
                await eval(instruction)
        else:
            self.logger.log(
                f"Command not implemented: {cmd.msg} / {cmd.data}",
                LogLevels.WARNING,
            )
