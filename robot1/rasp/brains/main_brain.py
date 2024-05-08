# External imports
import asyncio
import time
import math

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from led_strip import LEDStrip
from utils import Utils
from GPIO import PIN

# Import from local path
from brains.acs import AntiCollisionMode, AntiCollisionHandle
from controllers import RollingBasis, Actuators
from sensors import Lidar


class MainBrain(Brain):
    """
    This brain is the main controller of ROB (robot1).
    """

    # Controllers functions
    from brains.controllers_brain import (
        deploy_god_hand,
        undeploy_god_hand,
        open_god_hand,
        close_god_hand,
        go_best_zone,
        god_hand_demo,
        smart_go_to,
        vertical_god_hand,
        deploy_right_solar_panel,
        undeploy_right_solar_panel,
        deploy_left_solar_panel,
        undeploy_left_solar_panel,
        deploy_team_solar_panel,
        undeploy_team_solar_panel,
        avoid_obstacle,
    )

    # Sensors functions
    from brains.sensors_brain import (
        compute_ennemy_position,
        pol_to_abs_cart,
        get_ennemy_angle,
    )

    # Com functions
    from brains.com_brain import zombie_mode

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        ws_pami: WServerRouteManager,
        actuators: Actuators,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        logger_arena: Logger,
        jack: PIN,
        team_switch: PIN,
        leds: LEDStrip,
    ) -> None:

        self.anticollision_mode: AntiCollisionMode = AntiCollisionMode(
            CONFIG.ANTICOLLISION_MODE
        )
        self.anticollision_handle: AntiCollisionHandle = AntiCollisionHandle(
            CONFIG.ANTICOLLISION_HANDLE
        )

        # Save this for later use (when re-creating the arena)
        self.logger_arena: Logger

        self.rolling_basis: RollingBasis
        self.jack: PIN
        self.leds: LEDStrip
        self.team_switch: PIN

        # Init the brain
        super().__init__(logger, self)

        # A default, almost dummy starting situation
        self.team = CONFIG.DEFAULT_TEAM
        self.arena: MarsArena = self.generate_up_to_date_arena()
        self.reset_odo_to_start()

        # The regularly updated variable to estimate time left
        self.return_eta: float = -1.0

        self.score_estimate: int = 0

        # Init CONFIG
        self.logger.log(
            f"Mode: {'zombie' if CONFIG.ZOMBIE_MODE else 'game'}", LogLevels.INFO
        )

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=False)
    async def setup_actuators(self):
        await self.undeploy_god_hand()
        await self.close_god_hand()
        await self.undeploy_right_solar_panel()
        await self.undeploy_left_solar_panel()

    @Brain.task(process=False, run_on_start=False)
    async def wait_for_trigger(self):
        # Check jack state
        self.leds.set_jack(False)
        while self.jack.digital_read():
            await self.show_team_led()
            await asyncio.sleep(0.1)
        self.leds.set_jack(True)

    @Brain.task(process=False, run_on_start=False)
    async def setup_teams(self):
        self.get_team_from_switch()

        start_zone_id = CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"]
        self.logger.log(f"Team {self.team}", LogLevels.INFO)

        self.leds.set_team(self.team)

        self.logger.log(f"Game start, zone chosen: {start_zone_id}", LogLevels.INFO)

        # Arena
        self.arena = self.generate_up_to_date_arena()
        self.reset_odo_to_start()

    def reset_odo_to_start(self) -> None:
        self.rolling_basis.set_odo(
            OrientedPoint(
                (
                    CONFIG.START_INFO_BY_TEAM[self.team]["start_x"],
                    CONFIG.START_INFO_BY_TEAM[self.team]["start_y"],
                ),
                CONFIG.START_INFO_BY_TEAM[self.team]["start_theta"],
            )
        )

    def generate_up_to_date_arena(self) -> MarsArena:
        return MarsArena(
            CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"],
            logger=self.logger_arena,
            border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
            robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
        )

    def get_team_from_switch(self) -> None:
        if self.team_switch.digital_read():
            self.team = CONFIG.TEAM_SWITCH_ON
        else:
            self.team = CONFIG.TEAM_SWITCH_OFF

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE)
    async def start(self):
        await self.setup_actuators()

        self.logger.log("Waiting for jack trigger...", LogLevels.INFO, self.leds)

        await self.wait_for_trigger()
        await self.setup_teams()

        # Solar panels stage
        self.logger.log("Starting solar panels stage...", LogLevels.INFO, self.leds)
        await self.solar_panels_stage()

        # Plant Stage
        self.logger.log("Starting plant stage...", LogLevels.INFO, self.leds)
        await self.plant_stage()

        # Clean up
        await self.endgame()
        self.logger.log("Game over", LogLevels.INFO, self.leds)
        exit()

    async def show_team_led(self):
        self.get_team_from_switch()
        self.leds.set_team(self.team)

    async def undeploy_all(self):
        await self.close_god_hand()
        await self.vertical_god_hand()
        await self.undeploy_left_solar_panel()
        await self.undeploy_right_solar_panel()

    async def back_and_forth(self, distance: float = 50.0):
        await self.rolling_basis.go_to_and_wait(
            Point(distance, 0.0),
            forward=True,
            max_speed=160,
            next_position_delay=100,
            action_error_auth=100,
            traj_precision=50,
            correction_trajectory_speed=0,
            acceleration_start_speed=160,
            acceleration_distance=0,
            deceleration_end_speed=160,
            deceleration_distance=0,
            relative=True,
        )

        await asyncio.sleep(2)
        await self.rolling_basis.go_to_and_wait(
            Point(-distance, 0.0),
            forward=True,
            max_speed=160,
            next_position_delay=100,
            action_error_auth=100,
            traj_precision=50,
            correction_trajectory_speed=0,
            acceleration_start_speed=160,
            acceleration_distance=0,
            deceleration_end_speed=160,
            deceleration_distance=0,
            relative=True,
        )

    async def endgame(self):
        # Keep kill_rolling_basis outside a try to be absolutely sure to get to it
        try:
            # Open and deploy god hand, to macimize odds of being in home zone and to let go af any plant still held by accident
            await self.deploy_god_hand()
            await self.open_god_hand()
        except Exception:
            pass
        finally:
            await self.kill_rolling_basis()

    async def go_and_pickup(
        self,
        target_pickup_zone: Plants_zone,
        distance_from_zone=15,
        distance_final_approach=10,
    ) -> int:
        await self.deploy_god_hand()
        await self.open_god_hand()

        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=target_pickup_zone.zone,
            delta=distance_from_zone,
        )

        if (
            await self.smart_go_to(
                position=target,
                timeout=30,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"],
            )
            != 0
        ):
            self.logger.log("Failed", LogLevels.ERROR, self.leds)
            return 1
        else:
            # Final approach
            await self.smart_go_to(
                Point(distance_final_approach, 0),
                timeout=10,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"],
                relative=True,
            )

            # Grab plants
            await self.close_god_hand()
            await asyncio.sleep(0.2)
            await self.undeploy_god_hand()

            # Account for removed plants
            target_pickup_zone.take_plants(5)

            # Step back
            if (
                await self.smart_go_to(
                    Point(-100, 0),
                    timeout=10,
                    forward=False,
                    **CONFIG.SPEED_PROFILES["cruise_speed"],
                    **CONFIG.PRECISION_PROFILES["classic_precision"],
                    relative=True,
                )
                != 0
            ):
                self.logger.log("Failed", LogLevels.ERROR, self.leds)
                return 2
            else:
                self.logger.log("Success", LogLevels.INFO, self.leds)
                return 0

    async def go_and_drop(self, target_drop_zone: Plants_zone) -> int:  # TODO

        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie, zone=target_drop_zone.zone
        )

        if (
            await self.smart_go_to(
                position=target,
                timeout=30,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"],
            )
            != 0
        ):
            self.logger.log("Failed", LogLevels.ERROR, self.leds)
            return 1
        else:

            # Drop plants
            await self.deploy_god_hand()
            await self.open_god_hand()

            # Account for removed plants
            target_drop_zone.drop_plants(5)

            # Step back
            if (
                await self.smart_go_to(
                    Point(-30, 0),
                    timeout=10,
                    forward=False,
                    **CONFIG.SPEED_PROFILES["cruise_speed"],
                    **CONFIG.PRECISION_PROFILES["classic_precision"],
                    relative=True,
                )
                != 0
            ):
                self.logger.log("Failed", LogLevels.ERROR, self.leds)
                return 2
            else:
                self.logger.log("Success", LogLevels.INFO, self.leds)
                return 0

    @Brain.task(process=False, run_on_start=False, timeout=60)
    async def plant_stage(self):
        start_stage_time = Utils.get_ts()
        in_yellow_team = self.team == "y"

        # Closest pickup zone
        pickup_target: Plants_zone = self.arena.pickup_zones[0 if in_yellow_team else 4]
        self.logger.log(
            f"Going to pickup zone {0 if in_yellow_team else 4}",
            LogLevels.INFO,
            self.leds,
        )
        await self.go_and_pickup(pickup_target)

        drop_target: Plants_zone = self.arena.drop_zones[0 if in_yellow_team else 3]

        self.logger.log(
            f"Going to drop zone {0 if in_yellow_team else 3}",
            LogLevels.INFO,
            self.leds,
        )
        await self.go_and_drop(drop_target)

        # Next pickup zone
        pickup_target = self.arena.pickup_zones[1 if in_yellow_team else 3]

        self.logger.log(
            f"Going to pickup zone {1 if in_yellow_team else 3}",
            LogLevels.INFO,
            self.leds,
        )
        await self.go_and_pickup(pickup_target)

        drop_target = self.arena.drop_zones[2 if in_yellow_team else 5]

        self.logger.log(
            f"Going to drop zone {2 if in_yellow_team else 5}",
            LogLevels.INFO,
            self.leds,
        )
        await self.go_and_drop(drop_target)

        self.score_estimate += 20

    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def solar_panels_stage(self) -> None:
        asyncio.create_task(self.control_solar_panels())
        go_to_result = await self.rolling_basis.go_to_and_wait(
            Point(80, 0),
            relative=True,
            timeout=15.0,
            **CONFIG.SPEED_PROFILES["low_speed"],
            **CONFIG.PRECISION_PROFILES["classic_precision"],
        )

        if go_to_result == 0:
            # Great success!
            self.score_estimate += 15
        elif go_to_result == 1:
            # Timed out
            self.score_estimate += 5
        else:
            # ACS triggered
            self.score_estimate += 10

    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def control_solar_panels(self, solar_panel_timeout: float = 25.0) -> None:
        solar_panels_y: list[float] = [30, 50, 70]
        start_time = Utils.get_ts()
        while Utils.time_since(start_time) < solar_panel_timeout:
            await asyncio.sleep(0.1)
            if (
                min([abs(self.rolling_basis.odometrie.y - y) for y in solar_panels_y])
                > 5
            ):
                await self.deploy_team_solar_panel()

    @Brain.task(process=False, run_on_start=False, timeout=30)
    async def old_solar_panels_stage(self) -> int:
        solar_panels_distances = [26, 21, 21]

        for i in range(len(solar_panels_distances)):
            self.logger.log(f"Doing solar panel {i}", LogLevels.INFO, self.leds)
            await self.deploy_team_solar_panel()
            go_to_result = await self.rolling_basis.go_to_and_wait(
                Point(solar_panels_distances[i], 0),
                relative=True,
                timeout=7.0,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"],
            )

            if go_to_result != 0:
                self.logger.log(
                    f"Error going to solar panel {i}, go_to_and_wait returned: {go_to_result}",
                    LogLevels.WARNING,
                    self.leds,
                )
                break
            self.logger.log(f"Finished solar panel {i}", LogLevels.INFO, self.leds)

        await self.undeploy_team_solar_panel()
        return go_to_result

    @Brain.task(process=False, run_on_start=True, refresh_rate=2)
    async def update_return_eta(self):

        target = self.compute_return_target()

        delta = distance(self.rolling_basis.odometrie, target)
        self.return_eta = 5 + 0.05 * delta
        self.logger.log(f"Estimated ETA: {self.return_eta}", LogLevels.DEBUG)

    def compute_return_target(self):
        sorted_zones = self.arena.sort_drop_zone(
            self.rolling_basis.odometrie, friendly_only=True, maxi_plants=20
        )

        picked_zone = (
            sorted_zones[0]
            if sorted_zones[0]
            == self.arena.drop_zones[
                CONFIG.START_INFO_BY_TEAM[self.team]["start_zone_id"]
            ]
            else sorted_zones[1]
        )

        return self.arena.compute_go_to_destination(
            self.rolling_basis.odometrie,
            picked_zone.zone,
            20.0,
        )

    @Brain.task(process=False, run_on_start=False)
    async def kill_rolling_basis(self, timeout=-1):
        if timeout > 0:
            await asyncio.sleep(timeout)

        self.logger.log("Killing rolling basis", LogLevels.WARNING)
        self.rolling_basis.stop_and_clear_queue()
        self.rolling_basis.set_pids(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.rolling_basis = None
