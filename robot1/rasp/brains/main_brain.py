# External imports
import asyncio
import time

# Import from common
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager
from geometry import OrientedPoint, Point
from logger import Logger, LogLevels
from arena import MarsArena
from utils import Utils

# Import from local path
from controllers import RollingBasis, Actuators
from sensors import Lidar


class MainBrain(Brain):
    """
    This brain is the main controller of ROB (robot1).
    """

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
        # Camera data
        self.arucos = []
        self.green_objects = []

        # Init the brain
        super().__init__(logger, self)

    # Controllers functions
    from brains.controllers_brain import (
        deploy_god_hand,
        undeploy_god_hand,
        open_god_hand,
        close_god_hand,
        go_best_zone,
    )

    # Sensors functions
    from brains.sensors_brain import compute_ennemy_position, pol_to_abs_cart

    """
        Secondary routines
    """

    """ Subprocess routines """
    # ...

    """ Main process routines """
    from brains.com_brain import camera_com, odometer_com, zombie_mode

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=False, refresh_rate=5, timeout=2000)
    async def test_hand(self):
        self.logger.log("Open hand", LogLevels.INFO)
        await self.open_god_hand()
        await asyncio.sleep(5)
        self.logger.log("Close hand", LogLevels.INFO)
        await self.close_god_hand()

    @Brain.task(process=False, run_on_start=False, timeout=300)
    async def plant_stage(self):
        start_stage_time = Utils.get_ts()
        while 300 - Utils.time_since(start_stage_time) > 10:
            is_arrived: bool = False
            await self.open_god_hand()
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

                if is_arrived and destination_plant_zone is not None:
                    # Grab plants
                    await self.close_god_hand()
                    await asyncio.sleep(0.2)
                    # Account for removed plants
                    destination_plant_zone.take_plants(5)
                    # Step back
                    await self.rolling_basis.go_to(
                        Point(-15, 0), is_forward=False, relative=True
                    )

            is_arrived = False
            while not is_arrived:
                self.logger.log("Sorting drop zones...", LogLevels.INFO)
                plant_zones = self.arena.sort_drop_zone(self.rolling_basis.odometrie)
                self.logger.log("Going to best drop zone...", LogLevels.INFO)
                is_arrived, destination_plant_zone = await self.go_best_zone(
                    plant_zones, delta=25
                )
                self.logger.log(
                    (
                        f"Finished go_best_zone: " + "arrived"
                        if is_arrived
                        else "did not arrive"
                    ),
                    LogLevels.INFO,
                )
                if is_arrived and destination_plant_zone is not None:
                    await self.rolling_basis.go_to(
                        Point(10, 0), max_speed=50, relative=True
                    )
                    # Drop plants
                    await self.open_god_hand()
                    await asyncio.sleep(0.2)
                    # Account for new plants
                    destination_plant_zone.drop_plants(5)
