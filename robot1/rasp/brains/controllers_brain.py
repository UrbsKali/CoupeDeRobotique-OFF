# External imports
import asyncio

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import OrientedPoint, Point
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels

# Import from local path
from controllers import RollingBasis, Actuators


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
    for servo in FRONT_GOD_HAND:
        self.actuators.update_servo(servo["pin"], servo["open_angle"])


@Logger
def close_god_hand(self):
    for servo in FRONT_GOD_HAND:
        self.actuators.update_servo(servo["pin"], servo["close_angle"])


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
