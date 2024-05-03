# External imports
import asyncio
import time
import math

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point
from logger import Logger, LogLevels
from arena import MarsArena, Plants_zone
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
    ) -> None:

        self.team = arena.team
        self.rolling_basis: RollingBasis
        self.arena: MarsArena
        self.jack: PIN
        self.anticollision_mode: AntiCollisionMode = AntiCollisionMode(
            CONFIG.ANTICOLLISION_MODE
        )
        self.anticollision_handle: AntiCollisionHandle = AntiCollisionHandle(
            CONFIG.ANTICOLLISION_HANDLE
        )

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
        self.logger.log("Game start, waiting for jack trigger...", LogLevels.INFO)

        # Check jack state
        while self.jack.digital_read():
            await asyncio.sleep(0.1)

        # Plant Stage
        self.logger.log("Starting plant stage...", LogLevels.INFO)
        await self.plant_stage()

        await self.kill_rolling_basis()

        self.logger.log(f"Game over", LogLevels.INFO)

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

    async def go_and_drop(
        self,
        target_drop_zone: Plants_zone,
        distance_from_zone=25,
        distance_final_approach=10,
    ) -> int:  # TODO

        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=target_drop_zone.zone,
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

            # Drop plants
            await self.deploy_god_hand()
            await self.open_god_hand()

            # Account for removed plants
            target_drop_zone.drop_plants(5)

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
