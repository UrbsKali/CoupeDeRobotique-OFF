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

        self.rolling_basis: RollingBasis
        self.arena: MarsArena
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
    )

    # Sensors functions
    from brains.sensors_brain import (
        compute_ennemy_position,
        pol_to_abs_cart,
        get_angle_ennemy,
    )

    # Com functions
    from brains.com_brain import zombie_mode

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=not CONFIG.ZOMBIE_MODE)
    async def start(self):
        if CONFIG.ENABLE_TEAM_SWITCH:
            if self.team_switch.digital_read():
                start_zone_id = CONFIG.TEAM_SWITCH_ON
                self.leds.set_team("y")
            else:
                start_zone_id = CONFIG.TEAM_SWITCH_OFF
                self.leds.set_team("b")
            self.logger.log(
                f"Game start, zone chosen by switch : {start_zone_id}", LogLevels.INFO
            )
        else:
            self.logger.log(
                "Game start, waiting for start info from RC...", LogLevels.INFO
            )
            # Wait for RC start info
            zone = await self.ws_cmd.receiver.get()
            while zone == WSmsg() and zone.msg != "zone":
                zone = await self.ws_cmd.receiver.get()
                await asyncio.sleep(0.2)

            start_zone_id = zone.data
            self.logger.log(
                f"Got start zone: {start_zone_id}, re-initializing arena and resetting odo...",
                LogLevels.INFO,
            )

        self.rolling_basis.set_odo(
            OrientedPoint.from_Point(
                self.arena.zones["home"].centroid,
                math.pi / 2 if start_zone_id <= 2 else -math.pi / 2,
            )
        )

        self.logger.log("Waiting for jack trigger...", LogLevels.INFO)

        # Check jack state
        while self.jack.digital_read():
            await asyncio.sleep(0.1)
        self.leds.set_jack(True)

        # Plant Stage
        self.logger.log("Starting plant stage...", LogLevels.INFO)
        await self.plant_stage()

        await self.kill_rolling_basis()

        self.logger.log("Game over", LogLevels.INFO)

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
                return 2
            else:
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
                return 2
            else:
                return 0

    @Brain.task(process=False, run_on_start=False, timeout=100)
    async def plant_stage(self):
        start_stage_time = Utils.get_ts()
        in_yellow_team = self.team == "y"

        # Closest pickup zone
        pickup_target: Plants_zone = self.arena.pickup_zones[0 if in_yellow_team else 4]
        self.logger.log(
            f"Going to pickup zone {0 if in_yellow_team else 4}", LogLevels.INFO
        )
        await self.go_and_pickup(pickup_target)

        drop_target: Plants_zone = self.arena.drop_zones[0 if in_yellow_team else 3]

        self.logger.log(
            f"Going to drop zone {0 if in_yellow_team else 3}", LogLevels.INFO
        )
        await self.go_and_drop(drop_target)

        # Next pickup zone
        pickup_target = self.arena.pickup_zones[1 if in_yellow_team else 3]

        self.logger.log(
            f"Going to pickup zone {1 if in_yellow_team else 3}", LogLevels.INFO
        )
        await self.go_and_pickup(pickup_target)

        drop_target = self.arena.drop_zones[2 if in_yellow_team else 5]

        self.logger.log(
            f"Going to drop zone {2 if in_yellow_team else 5}", LogLevels.INFO
        )
        await self.go_and_drop(drop_target)

    @Brain.task(process=False, run_on_start=False)
    async def kill_rolling_basis(self, timeout=-1):
        if timeout > 0:
            await asyncio.sleep(timeout)

        self.logger.log("Killing rolling basis", LogLevels.WARNING)
        self.rolling_basis.stop_and_clear_queue()
        self.rolling_basis.set_pid(0.0, 0.0, 0.0)
        self.rolling_basis = None
