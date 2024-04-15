# External imports
# ..

# Import from common
from config_loader import CONFIG

from brain import Brain

from WS_comms import WSmsg, WServerRouteManager
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
        self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

        # Handle it (implemented only for Go_To and Keep_Current_Position)
        if cmd.msg == "go_to":
            self.rolling_basis.clear_queue()
            self.rolling_basis.go_to(
                position=Point(cmd.data[0], cmd.data[1]),
                max_speed=cmd.data[2],
                next_position_delay=cmd.data[3],
                action_error_auth=cmd.data[4],
                traj_precision=cmd.data[5],
                correction_trajectory_speed=cmd.data[6],
                acceleration_start_speed=cmd.data[7],
                acceleration_distance=cmd.data[8],
                deceleration_end_speed=cmd.data[9],
                deceleration_distance=cmd.data[10],
            )
        elif cmd.msg == "keep_current_position":
            self.rolling_basis.clear_queue()
            self.rolling_basis.keep_current_pos()

        elif cmd.msg == "set_pid":
            self.rolling_basis.clear_queue()
            self.rolling_basis.set_pid(Kp=cmd.data[0], Ki=cmd.data[1], Kd=cmd.data[2])
        elif cmd.msg == "go_to_and_wait":
            await self.rolling_basis.go_to_and_wait(
                position=Point(cmd.data[0], cmd.data[1]),
                timeout=cmd.data[2],
                tolerance=cmd.data[3],
            )
        elif cmd.msg == "eval":

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
