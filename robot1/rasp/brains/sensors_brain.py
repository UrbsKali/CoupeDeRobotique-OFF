# External imports
import numpy as np
import asyncio
import math

# Import from common
from config_loader import CONFIG

from brain import Brain

from geometry import OrientedPoint, Point, MultiPoint, is_empty, nearest_points
from WS_comms import WSmsg, WSclientRouteManager
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels

# Import from local path
from sensors import Lidar
from brains.acs import AntiCollisionMode, AntiCollisionHandle


def get_ennemy_angle(self, relative=False):
    angle_abs = math.degrees(
        math.atan(
            (self.arena.ennemy_position.x - self.rolling_basis.odometrie.x)
            / (self.arena.ennemy_position.y - self.rolling_basis.odometrie.y)
        )
        - self.rolling_basis.odometrie.theta
    )

    return angle_abs if not relative else angle_abs - self.rolling_basis.odometrie.theta


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def compute_ennemy_position(self):
    polars: np.ndarray = self.lidar.scan_to_polars()
    # self.logger.log(f"Polars ({polars.shape}): {polars.tolist()}", LogLevels.INFO)
    obstacles: MultiPoint | Point = self.arena.remove_outside(
        self.pol_to_abs_cart(polars)
    )

    # self.logger.log(f"obstacles: {obstacles}", LogLevels.INFO)

    # asyncio.create_task(
    #     self.ws_lidar.sender.send(
    #         WSmsg(
    #             msg="obstacles",
    #             data=(
    #                 []
    #                 if is_empty(obstacles)
    #                 else (
    #                     [(geom.x, geom.y) for geom in obstacles.geoms]
    #                     if isinstance(obstacles, MultiPoint)
    #                     else (obstacles.x, obstacles.y)
    #                 )
    #             ),
    #         )
    #     )
    # )

    # For now, the closest will be the enemy position
    self.arena.ennemy_position = (
        None
        if is_empty(obstacles)
        else nearest_points(self.rolling_basis.odometrie, obstacles)[1]
    )

    self.logger.log(
        f"Ennemy position computed: {self.arena.ennemy_position if self.arena.ennemy_position is not None else 'None'}, at absolute/relative angle: {(round(self.get_ennemy_angle()) + '/' + round(self.get_ennemy_angle(relative=True))) if self.arena.ennemy_position is not None else 'None'} and distance: {math.sqrt(pow(self.arena.ennemy_position.x - self.rolling_basis.odometrie.x,2)+pow(self.arena.ennemy_position.y - self.rolling_basis.odometrie.y,2)) if self.arena.ennemy_position is not None else 'None'}",
        LogLevels.DEBUG,
    )

    # For now, just stop if close. When updating, consider self.arena.check_collision_by_distances
    if (
        self.anticollision_mode != AntiCollisionMode.DISABLED
        and self.arena.ennemy_position is not None
    ):
        if (
            self.rolling_basis.odometrie.distance(self.arena.ennemy_position)
            < CONFIG.STOP_TRESHOLD
        ):
            if self.anticollision_mode == AntiCollisionMode.CIRCULAR:
                self.logger.log(
                    "ACS triggered, performing emergency stop", LogLevels.WARNING
                )
                self.rolling_basis.stop_and_clear_queue()
                self.leds.acs_state(True)
            if self.anticollision_mode == AntiCollisionMode.FRONTAL:
                if (
                    abs(self.get_ennemy_angle(relative=True))
                    < CONFIG.LIDAR_FRONTAL_DETECTION_ANGLE
                ):
                    self.logger.log(
                        "ACS triggered, performing emergency stop", LogLevels.WARNING
                    )
                    self.rolling_basis.stop_and_clear_queue()
                    self.leds.acs_state(True)
            if self.anticollision_mode == AntiCollisionMode.SEMI_CIRCULAR:
                if (
                    abs(self.get_ennemy_angle(relative=True))
                    < CONFIG.LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE
                ):
                    self.logger.log(
                        "ACS triggered, performing emergency stop", LogLevels.WARNING
                    )
                    self.rolling_basis.stop_and_clear_queue()
                    self.leds.acs_state(True)

        else:
            # self.logger.log("ACS not triggered", LogLevels.DEBUG)
            self.leds.acs_state(False)


def pol_to_abs_cart(self, polars: np.ndarray) -> MultiPoint:
    return MultiPoint(
        [
            (
                self.rolling_basis.odometrie.x
                + np.cos(self.rolling_basis.odometrie.theta + polars[i, 0])
                * polars[i, 1],
                self.rolling_basis.odometrie.y
                + np.sin(self.rolling_basis.odometrie.theta + polars[i, 0])
                * polars[i, 1],
            )
            for i in range(len(polars))
        ]
    )


@Brain.task(process=False, run_on_start=True, refresh_rate=2)
async def print_odometer(self):
    self.logger.log(
        f"Odometer: {self.rolling_basis.odometrie}",
        LogLevels.DEBUG,
    )
