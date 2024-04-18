# External imports
import asyncio
import time

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import OrientedPoint, Point
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels

# Import from local path
from controllers import RollingBasis, Actuators


@Logger
async def deploy_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    self.actuators.update_servo(servo["pin"], servo["deploy_angle"])


@Logger
async def undeploy_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    self.actuators.update_servo(servo["pin"], servo["undeploy_angle"])


@Logger
async def open_god_hand(self):
    for servo in CONFIG.FRONT_GOD_HAND["take_servo"]:
        await asyncio.sleep(CONFIG.MINIMUM_DELAY)
        self.actuators.update_servo(servo["pin"], servo["open_angle"])


@Logger
async def close_god_hand(self):
    for servo in CONFIG.FRONT_GOD_HAND["take_servo"]:
        await asyncio.sleep(CONFIG.MINIMUM_DELAY)
        self.actuators.update_servo(servo["pin"], servo["close_angle"])


async def god_hand_demo(self):
    while True:
        await self.undeploy_god_hand()
        await asyncio.sleep(1)
        await self.deploy_god_hand()
        await asyncio.sleep(1)
        await self.open_god_hand()
        await asyncio.sleep(1)
        await self.close_god_hand()
        await asyncio.sleep(1)
        await self.undeploy_god_hand()
        await asyncio.sleep(1)


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
        and (await self.rolling_basis.go_to_and_wait(
            position=destination_point,
            timeout=30,
            **CONFIG.SPEED_PROFILES["cruise_speed"],
            **CONFIG.PRECISION_PROFILES["classic_precision"]
        ))
        == 0
    ):
        return True, destination_plant_zone
    return False, destination_plant_zone
