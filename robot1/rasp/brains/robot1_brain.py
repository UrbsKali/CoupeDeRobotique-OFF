# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSclientRouteManager, WSmsg
from brain import Brain
from utils import Utils

# Import from local path
from sensors import Lidar
from controllers import RollingBasis


class Robot1Brain(Brain):
    def __init__(
        self,
        logger: Logger,
        ws_cmd: WSclientRouteManager,
        ws_log: WSclientRouteManager,
        ws_lidar: WSclientRouteManager,
        ws_odometer: WSclientRouteManager,
        ws_camera: WSclientRouteManager,
        rolling_basis: RollingBasis,
        lidar: Lidar,
        arena: MarsArena,
    ) -> None:
        super().__init__(logger, self)

        # self.lidar_scan = []
        self.lidar_values_in_distances = []
        self.lidar_angles = (90, 180)
        self.odometer = None
        self.camera = {}

    """
        Routines
    """

    """
        Get controllers / sensors feedback (odometer / lidar + extern (camera))
    """

    async def ACS_by_distances(self):
        if self.arena.check_collision_by_distances(
            self.lidar_values_in_distances, self.odometer
        ):
            self.rolling_basis.Stop_and_clear_queue()
            # It is the currently runing action's responsibility to detect the stop

    @Brain.task(refresh_rate=0.5)
    async def lidar_scan_distance(self):
        # Warning, currently hard-coded for 3 values/degree
        self.lidar_values_in_distances = self.lidar.scan_distances(
            robot_pos=self.rolling_basis.odometrie,
            start_angle=self.lidar_angles[0],
            end_angle=self.lidar_angles[1],
        )

        self.ACS_by_distances()

    # @Brain.task(refresh_rate=0.5)
    # async def lidar_scan(self):
    #     scan = self.lidar.scan_to_absolute_cartesian(
    #         robot_pos=self.rolling_basis.odometrie
    #     )

    #     self.lidar_scan = [[p.x, p.y] for p in scan]

    @Brain.task(refresh_rate=0.5)
    async def odometer_update(self):
        self.odometer = OrientedPoint(
            self.rolling_basis.odometrie.x,
            self.rolling_basis.odometrie.y,
            self.rolling_basis.odometrie.theta,
        )

    @Brain.task(refresh_rate=0.5)
    async def get_camera(self):
        msg = await self.ws_camera.receiver.get()
        if msg != WSmsg():
            self.camera = msg.data

    """
        Send controllers / sensors feedback (odometer / lidar)
    """

    # @Brain.task(refresh_rate=1)
    # async def send_lidar_scan_to_server(self):
    #     if self.lidar_scan:
    #         await self.ws_lidar.sender.send(
    #             WSmsg(msg="lidar_scan", data=self.lidar_scan)
    #         )

    @Brain.task(refresh_rate=1)
    async def send_odometer_to_server(self):
        if self.odometer is not None:
            await self.ws_odometer.sender.send(
                WSmsg(msg="odometer", data=self.odometer)  # To check
            )

    @Brain.task(refresh_rate=0.1)
    async def main(self):
        # Check cmd
        cmd = await self.ws_cmd.receiver.get()

        if cmd != WSmsg():
            self.logger.log(f"New cmd received: {cmd}", LogLevels.INFO)

            # Handle it (implemented only for Go_To and Keep_Current_Position)
            if cmd.msg == "Go_To":
                self.rolling_basis.queue = []
                self.rolling_basis.Go_To(
                    OrientedPoint(cmd.data[0], cmd.data[1], cmd.data[2]),
                    skip_queue=True,
                )
            elif cmd.msg == "Keep_Current_Position":
                self.rolling_basis.queue = []
                self.rolling_basis.Keep_Current_Position()
            else:
                self.logger.log(
                    f"Command not implemented: {cmd.msg} / {cmd.data}",
                    LogLevels.WARNING,
                )

    async def go_to_and_wait_test(self):
        result = await self.rolling_basis.Got_To_And_Wait(
            Point(50, 50), tolerance=5, timout=20
        )

        if result == 0:
            self.logger.log("Success of movement test")
        elif result == 1:
            self.logger.log("Timed out of movement test")
        elif result == 2:
            self.logger.log("Error moving: didn't reach destination")
