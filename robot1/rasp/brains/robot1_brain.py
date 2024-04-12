# Import from common
import numpy as np
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena, Plants_zone
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils
import numpy as np

# Import from local path
from sensors import Lidar
from controllers import RollingBasis, Actuators
import asyncio
from geometry import Polygon, MultiPoint, nearest_points, is_empty
from config_loader import CONFIG
import time
import math


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Logger,
        ws_cmd: WSclientRouteManager,
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        actuators: Actuators,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        arena: MarsArena,
    ) -> None:

        self.camera = {}

        # to delete, only use for completion
        # self.rolling_basis:  RollingBasis
        # self.actuators: Actuators
        # self.arena: MarsArena
        # self.lidar:  Lidar

        super().__init__(logger, self)

        self.logger.log(
            f"Robot1 Brain initialized, current position: {1}",
            LogLevels.INFO,
        )

    """
        Routines
    """

    """
        Get controllers / sensors feedback (odometer / lidar + extern (camera))
    """

    # def ACS_by_distances(self):
    #     if self.arena.check_collision_by_distances(
    #         self.lidar_values_in_distances, self.rolling_basis.odometrie
    #     ):
    #         self.logger.log(
    #             "ACS triggered, performing emergency stop", LogLevels.WARNING
    #         )
    #         self.rolling_basis.stop_and_clear_queue()
    #         # It is the currently running action's responsibility to detect the stop if it needs to
    #     else:
    #         self.logger.log("ACS not triggered", LogLevels.DEBUG)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def get_camera(self):
        msg = await self.ws_camera.receiver.get()
        if msg != WSmsg():
            self.camera = msg.data

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def compute_ennemy_position(self):
        polars: np.ndarray = self.lidar.scan_to_polars()
        # self.logger.log(f"New measure", LogLevels.CRITICAL)
        # self.logger.log(f"Polars ({polars.shape}): {polars.tolist()}", LogLevels.INFO)
        obstacles: MultiPoint | Point = self.arena.remove_outside(
            self.pol_to_abs_cart(polars)
        )

        self.logger.log(f"obstacles: {obstacles}", LogLevels.INFO)

        asyncio.create_task(
            self.ws_lidar.sender.send(
                WSmsg(
                    msg="obstacles",
                    data=(np.array(obstacles.coords)),
                )
            )
        )

        # For now, the closest will be the enemy position
        self.arena.ennemy_position = (
            None
            if is_empty(obstacles)
            else nearest_points(self.rolling_basis.odometrie, obstacles)[1]
        )

        self.logger.log(
            f"Ennemy position computed: {self.arena.ennemy_position if self.arena.ennemy_position is not None else 'None'}, at angle: {math.degrees(math.atan((self.arena.ennemy_position.x - self.rolling_basis.odometrie.x)/(self.arena.ennemy_position.y - self.rolling_basis.odometrie.y))) if self.arena.ennemy_position is not None else 'None'} and distance: {math.sqrt(pow(self.arena.ennemy_position.x - self.rolling_basis.odometrie.x,2)+pow(self.arena.ennemy_position.y - self.rolling_basis.odometrie.y,2)) if self.arena.ennemy_position is not None else 'None'}",
            LogLevels.INFO,
        )

        # For now, just stop if close. When updating, consider self.arena.check_collision_by_distances
        if self.rolling_basis.odometrie.distance(self.arena.ennemy_position) < 40:
            self.logger.log(
                "ACS triggered, performing emergency stop", LogLevels.WARNING
            )
            self.rolling_basis.stop_and_clear_queue()
        else:
            self.logger.log("ACS not triggered", LogLevels.DEBUG)

    def pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
        return MultiPoint(
            [
                (
                    (
                        self.rolling_basis.odometrie.x
                        + np.cos(self.rolling_basis.odometrie.theta + polars[i, 0])
                        * polars[i, 1]
                    ),
                    self.rolling_basis.odometrie.y
                    + np.sin(self.rolling_basis.odometrie.theta + polars[i, 0])
                    * polars[i, 1],
                )
                for i in range(len(polars))
            ]
        )

    """
        Send controllers / sensors feedback (odometer / lidar)
    """

    # @Brain.task(refresh_rate=1)
    # async def send_lidar_scan_to_server(self):
    #     if self.lidar_scan:
    #         await self.ws_lidar.sender.send(
    #             WSmsg(msg="lidar_scan", data=self.lidar_scan)
    #         )

    @Brain.task(process=False, run_on_start=True, refresh_rate=1)
    async def send_odometer_to_server(self):
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

    @Brain.task(process=False, run_on_start=False)
    async def go_to_and_wait_test(self):
        await asyncio.sleep(1)
        result = await self.rolling_basis.go_to_and_wait(
            Point(50, 50), tolerance=5, timeout=20
        )

        if result == 0:
            self.logger.log("Success of movement test")
        elif result == 1:
            self.logger.log("Timed out of movement test")
        elif result == 2:
            self.logger.log("Error moving: didn't reach destination")

    @Logger
    def deploy_god_hand(self):
        self.actuators.update_servo(
            CONFIG.GOD_HAND_DEPLOYMENT_SERVO_PIN,
            CONFIG.GOD_HAND_DEPLOYMENT_SERVO_DEPLOY_ANGLE,
        )

    @Logger
    def undeploy_god_hand(self):
        self.actuators.update_servo(
            CONFIG.GOD_HAND_DEPLOYMENT_SERVO_PIN,
            CONFIG.GOD_HAND_DEPLOYMENT_SERVO_UNDEPLOY_ANGLE,
        )

    @Logger
    def open_god_hand(self):
        for pin in CONFIG.GOD_HAND_GRAB_SERVO_PINS_LEFT:
            self.actuators.update_servo(pin, CONFIG.GOD_HAND_GRAB_SERVO_OPEN_ANGLE)
        for pin in CONFIG.GOD_HAND_GRAB_SERVO_PINS_RIGHT:
            self.actuators.update_servo(pin, CONFIG.GOD_HAND_GRAB_SERVO_OPEN_ANGLE)

    @Logger
    def close_god_hand(self):
        for pin in CONFIG.GOD_HAND_GRAB_SERVO_PINS_LEFT:
            self.actuators.update_servo(
                pin,
                CONFIG.GOD_HAND_GRAB_SERVO_OPEN_ANGLE
                + CONFIG.GOD_HAND_GRAB_SERVO_CLOSE_ANGLE_DIFF_LEFT,
            )
        for pin in CONFIG.GOD_HAND_GRAB_SERVO_PINS_RIGHT:
            self.actuators.update_servo(
                pin,
                CONFIG.GOD_HAND_GRAB_SERVO_OPEN_ANGLE
                + CONFIG.GOD_HAND_GRAB_SERVO_CLOSE_ANGLE_DIFF_RIGHT,
            )

    async def go_best_zone(self, plant_zones: list[Plants_zone], delta=15):
        destination_point = None
        destination_plant_zone = None
        for plant_zone in plant_zones:
            target = self.arena.compute_go_to_destination(
                start_point=self.rolling_basis.odometrie,
                zone=plant_zone.zone,
                delta=delta,
            )
            if self.arena.enable_go_to_point(
                self.rolling_basis.odometrie,
                target,
            ):
                destination_point = target
                destination_plant_zone = plant_zone
                break
        if (
            destination_point != None
            and await self.rolling_basis.go_to_and_wait(
                position=destination_point, timeout=30
            )
            == 0
        ):
            return True, destination_plant_zone
        return False, destination_plant_zone

    @Brain.task(process=False, run_on_start=False, timeout=300)
    async def plant_stage(self):
        start_stage_time = Utils.get_ts()
        while 300 - Utils.time_since(start_stage_time) > 10:
            is_arrived: bool = False
            self.open_god_hand()
            while not is_arrived:
                self.logger.log("Sorting pickup zones...", LogLevels.INFO)
                plant_zones = self.arena.sort_pickup_zone(self.rolling_basis.odometrie)
                self.logger.log("Going to best pickup zone...", LogLevels.INFO)
                is_arrived, destination_plant_zone = await self.go_best_zone(
                    plant_zones
                )
                self.logger.log(
                    (
                        f"Finished go_best_zone: " + "arrived"
                        if is_arrived
                        else "did not arrive"
                    ),
                    LogLevels.INFO,
                )

                if is_arrived:
                    self.close_god_hand()
                    destination_plant_zone.take_plants(5)

            is_arrived = False
            while not is_arrived:
                self.logger.log("Sorting drop zones...", LogLevels.INFO)
                plant_zones = self.arena.sort_drop_zone(self.rolling_basis.odometrie)
                self.logger.log("Going to best drop zone...", LogLevels.INFO)
                is_arrived, destination_plant_zone = await self.go_best_zone(
                    plant_zones
                )
                self.logger.log(
                    (
                        f"Finished go_best_zone: " + "arrived"
                        if is_arrived
                        else "did not arrive"
                    ),
                    LogLevels.INFO,
                )
                if is_arrived:
                    self.open_god_hand()
                    destination_plant_zone.drop_plants(5)

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def zombie_mode(self):
        """executes requests received by the server. Use Postman to send request to the server
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
                self.rolling_basis.set_pid(
                    Kp=cmd.data[0], Ki=cmd.data[1], Kd=cmd.data[2]
                )
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
