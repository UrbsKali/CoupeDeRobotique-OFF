# External imports
import asyncio
import time
import math

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point
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

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        ws_pami: WServerRouteManager,
        actuators: Actuators,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        arena: MarsArena,
        jack: PIN,
        team_switch: PIN,
        leds: LEDStrip,
    ) -> None:
        self.team = arena.team
        self.anticollision_mode: AntiCollisionMode = AntiCollisionMode(
            CONFIG.ANTICOLLISION_MODE
        )
        self.anticollision_handle: AntiCollisionHandle = AntiCollisionHandle(
            CONFIG.ANTICOLLISION_HANDLE
        )
        self.arena: MarsArena = None

        self.rolling_basis: RollingBasis
        self.jack: PIN

        # Init the brain
        super().__init__(logger, self)

        # Init CONFIG
        self.logger.log(
            f"Mode: {'zombie' if CONFIG.ZOMBIE_MODE else 'game'}", LogLevels.INFO
        )

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
            await self.show_team_switch()
            await asyncio.sleep(0.1)
        self.leds.set_jack(True)

    @Brain.task(process=False, run_on_start=False)
    async def setup_teams(self):
        if self.team_switch.digital_read():
            start_zone_id = CONFIG.TEAM_SWITCH_ON
            self.logger.log("Team yellow", LogLevels.INFO)
            self.leds.set_team("y")
        else:
            start_zone_id = CONFIG.TEAM_SWITCH_OFF
            self.logger.log("Team blue", LogLevels.INFO)
            self.leds.set_team("b")
        self.logger.log(
            f"Game start, zone chosen by switch : {start_zone_id}", LogLevels.INFO
        )

        # Arena
        self.arena = MarsArena(
            start_zone_id,
            logger=logger_arena,
            border_buffer=CONFIG.ARENA_CONFIG["border_buffer"],
            robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"],
        )

        self.rolling_basis.set_odo(
            OrientedPoint.from_Point(
                self.arena.zones["home"].centroid,
                math.pi / 2 if start_zone_id <= 2 else -math.pi / 2,
            )
        )

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

    async def show_team_switch(self):
        if self.team_switch.digital_read():
            self.leds.set_team("y")
        else:
            self.leds.set_team("b")

    async def homologate1(self):
        await self.close_god_hand()
        await self.vertical_god_hand()

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
            self.log("Failed", LogLevels.ERROR, self.leds)
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
                self.log("Failed", LogLevels.ERROR, self.leds)
                return 2
            else:
                self.log("Success", LogLevels.INFO, self.leds)
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
            self.log("Failed", LogLevels.ERROR, self.leds)
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
                self.log("Failed", LogLevels.ERROR, self.leds)
                return 2
            else:
                self.log("Success", LogLevels.INFO, self.leds)
                return 0

    @Brain.task(process=False, run_on_start=False, timeout=100)
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

    async def solar_panels_stage(self) -> int:

        solar_panels_distances = [26, 21, 21]

        for i in range(len(solar_panels_distances)):
            self.logger.log(f"Doing solar panel {i}", LogLevels.INFO, self.leds)
            await self.deploy_team_solar_panel()
            go_to_result = await self.rolling_basis.go_to_and_wait(
                Point(solar_panels_distances[i], 0),
                relative=True,
                timeout=20.0,
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

        self.undeploy_team_solar_panel()
        return go_to_result

    @Brain.task(process=False, run_on_start=False)
    async def kill_rolling_basis(self, timeout=-1):
        if timeout > 0:
            await asyncio.sleep(timeout)

        self.logger.log("Killing rolling basis", LogLevels.WARNING)
        self.rolling_basis.stop_and_clear_queue()
        self.rolling_basis.set_pid(0.0, 0.0, 0.0)
        self.rolling_basis = None
