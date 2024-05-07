# External imports
import asyncio
import time

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import OrientedPoint, Point
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
from brains.acs import AntiCollisionMode, AntiCollisionHandle

# Import from local path
from controllers import RollingBasis, Actuators


@Logger
async def deploy_right_solar_panel(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_RIGHT
    self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["deploy_angle"],
        detach=True,
        detach_delay=servo["detach_delay"],
    )


@Logger
async def undeploy_right_solar_panel(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_RIGHT
    self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["undeploy_angle"],
        detach=True,
        detach_delay=servo["detach_delay"],
    )


@Logger
async def deploy_left_solar_panel(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_LEFT
    self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["deploy_angle"],
        detach=True,
        detach_delay=servo["detach_delay"],
    )


@Logger
async def undeploy_left_solar_panel(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.SOLAR_PANEL_LEFT
    self.actuators.update_servo(
        pin=servo["pin"],
        angle=servo["undeploy_angle"],
        detach=True,
        detach_delay=servo["detach_delay"],
    )


@Logger
async def deploy_team_solar_panel(self):
    if self.team == "y":
        await deploy_left_solar_panel()
    else:
        await deploy_right_solar_panel()


@Logger
async def undeploy_team_solar_panel(self):
    if self.team == "y":
        await undeploy_left_solar_panel()
    else:
        await undeploy_right_solar_panel()


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
async def vertical_god_hand(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    servo = CONFIG.FRONT_GOD_HAND["deployment_servo"]
    self.actuators.update_servo(servo["pin"], servo["vertical_angle"])


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


@Logger
async def lift_elevator(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    stepper = CONFIG.ELEVATOR
    self.actuators.stepper_step(
        steps=stepper["up_steps"],
        pin_dir=stepper["pin_dir"],
        pin_step=stepper["pin_step"],
        speed=stepper["speed"],
        driver_on=stepper["driver_on"],
        pin_driver=stepper["pin_driver"],
    )


async def lower_elevator(self):
    await asyncio.sleep(CONFIG.MINIMUM_DELAY)
    stepper = CONFIG.ELEVATOR
    self.actuators.stepper_step(
        steps=stepper["down_steps"],
        pin_dir=stepper["pin_dir"],
        pin_step=stepper["pin_step"],
        speed=stepper["speed"],
        driver_on=stepper["driver_on"],
        pin_driver=stepper["pin_driver"],
    )


async def god_hand_demo(self):
    while True:
        await self.vertical_god_hand()
        await asyncio.sleep(0.5)
        await self.undeploy_god_hand()
        await asyncio.sleep(0.5)
        await self.deploy_god_hand()
        await asyncio.sleep(1)
        await self.open_god_hand()
        await asyncio.sleep(1)
        await self.close_god_hand()
        await asyncio.sleep(1)
        await self.undeploy_god_hand()
        await asyncio.sleep(0.5)
        await self.vertical_god_hand()
        await asyncio.sleep(0.5)


async def smart_go_to(
    self,
    position: Point,
    *,  # force keyword arguments
    tolerance: float = 5,
    timeout: float = -1,  # in seconds
    skip_and_clear_queue: bool = False,
    forward: bool = True,
    relative: bool = False,
    max_speed: int = 160,
    next_position_delay: int = 100,
    action_error_auth: int = 30,
    traj_precision: int = 30,
    correction_trajectory_speed: int = 160,
    acceleration_start_speed: int = 160,
    acceleration_distance: float = 0,
    deceleration_end_speed: int = 160,
    deceleration_distance: float = 0,
    fails: int = 0
) -> int:

    result: int = await self.rolling_basis.go_to_and_wait(
        position,
        skip_and_clear_queue=skip_and_clear_queue,
        tolerance=tolerance,
        timeout=timeout,
        forward=forward,
        relative=relative,
        max_speed=max_speed,
        next_position_delay=next_position_delay,
        action_error_auth=action_error_auth,
        traj_precision=traj_precision,
        correction_trajectory_speed=correction_trajectory_speed,
        acceleration_start_speed=acceleration_start_speed,
        acceleration_distance=acceleration_distance,
        deceleration_end_speed=deceleration_end_speed,
        deceleration_distance=deceleration_distance,
    )
    if result == 2:
        # ACS handling strategy:
        result = await self.avoid_obstacle(
            position,
            skip_and_clear_queue=skip_and_clear_queue,
            tolerance=tolerance,
            timeout=timeout,
            forward=forward,
            relative=relative,
            max_speed=max_speed,
            next_position_delay=next_position_delay,
            action_error_auth=action_error_auth,
            traj_precision=traj_precision,
            correction_trajectory_speed=correction_trajectory_speed,
            acceleration_start_speed=acceleration_start_speed,
            acceleration_distance=acceleration_distance,
            deceleration_end_speed=deceleration_end_speed,
            deceleration_distance=deceleration_distance,
            fails=0,
        )

    return result


async def avoid_obstacle(
    self,
    original_target: Point,
    *,  # force keyword arguments
    skip_and_clear_queue: bool = False,
    tolerance: float = 5,
    timeout: float = -1,  # in seconds
    forward: bool = True,
    relative: bool = False,
    max_speed: int = 160,
    next_position_delay: int = 100,
    action_error_auth: int = 30,
    traj_precision: int = 30,
    correction_trajectory_speed: int = 160,
    acceleration_start_speed: int = 160,
    acceleration_distance: float = 0,
    deceleration_end_speed: int = 160,
    deceleration_distance: float = 0,
    fails: int = 0
) -> int:
    if self.anticollision_handle == AntiCollisionHandle.NOTHING:
        return 2
    elif self.anticollision_handle == AntiCollisionHandle.WAIT_AND_FAIL:
        await asyncio.sleep(5)
        return 2
    elif self.anticollision_handle == AntiCollisionHandle.WAIT_AND_RETRY and fails < 2:
        await asyncio.sleep(2)
        return await self.smart_go_to(
            original_target,
            skip_and_clear_queue=skip_and_clear_queue,
            tolerance=tolerance,
            timeout=timeout,
            forward=forward,
            relative=relative,
            max_speed=max_speed,
            next_position_delay=next_position_delay,
            action_error_auth=action_error_auth,
            traj_precision=traj_precision,
            correction_trajectory_speed=correction_trajectory_speed,
            acceleration_start_speed=acceleration_start_speed,
            acceleration_distance=acceleration_distance,
            deceleration_end_speed=deceleration_end_speed,
            deceleration_distance=deceleration_distance,
            fails=fails + 1,
        )
    else:
        raise Exception("No AntiCollisionHandle implementation?")


async def go_best_zone(self, plant_zones: list[Plants_zone]):
    destination_point = None
    destination_plant_zone = None
    for plant_zone in plant_zones:
        target = self.arena.compute_go_to_destination(
            start_point=self.rolling_basis.odometrie,
            zone=plant_zone.zone,
        )
        print("Target:", destination_point)
        # if self.arena.enable_go_to_point(
        #     self.rolling_basis.odometrie,
        #     target,
        # ):
        #     pass
        destination_point = target
        destination_plant_zone = plant_zone
        break
    print("Destination:", destination_point)
    if (
        destination_point != None
        and (
            await self.smart_go_to(
                position=destination_point,
                timeout=30,
                **CONFIG.SPEED_PROFILES["cruise_speed"],
                **CONFIG.PRECISION_PROFILES["classic_precision"]
            )
        )
        == 0
    ):
        return True, destination_plant_zone
    return False, destination_plant_zone
