# External imports
import asyncio
import time
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from arena import MarsArena
from WS_comms import WSmsg, WServerRouteManager
from brain import Brain
from video.server import MJPEGHandler

# Import from local path
from sensors import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame


class ServerBrain(Brain):
    """
    This brain is the main controller of the server.
    """

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        ws_pami: WServerRouteManager,
        ws_lidar: WServerRouteManager,
        ws_odometer: WServerRouteManager,
        ws_camera: WServerRouteManager,
        arena: MarsArena,
        config,
    ) -> None:
        # Camera data
        self.arucos = []
        self.green_objects = []

        # ROB data
        self.rob_pos: OrientedPoint | None = None
        self.lidar_points: list[Point] | None = None

        # Lidar display
        self.fig, self.ax = plt.subplots()
        self.xdata, self.ydata = [], []
        (self.ln,) = plt.plot([], [], "ro")

        # Init the brain
        super().__init__(logger, self)

    """
        Secondary routines
    """

    """ Subprocess routines """

    @Brain.task(
        process=True, run_on_start=True, refresh_rate=0.1, define_loop_later=True
    )
    def camera_capture(self):
        """
        Capture the camera image and detect arucos and green objects.
        """
        camera = Camera(
            res_w=self.config.CAMERA_RESOLUTION[0],
            res_h=self.config.CAMERA_RESOLUTION[1],
            captures_path=self.config.CAMERA_SAVE_PATH,
            undistorted_coefficients_path=self.config.CAMERA_COEFFICIENTS_PATH,
        )

        aruco_recognizer = ArucoRecognizer(
            aruco_type=self.config.CAMERA_ARUCO_DICT_TYPE
        )

        color_recognizer = ColorRecognizer(
            detection_range=self.config.CAMERA_COLOR_FILTER_RANGE,
            name=self.config.CAMERA_COLOR_FILTER_NAME,
            clustering_eps=self.config.CAMERA_COLOR_CLUSTERING_EPS,
            clustering_min_samples=self.config.CAMERA_COLOR_CLUSTERING_MIN_SAMPLES,
        )

        plan_transposer = PlanTransposer(
            camera_table_distance=self.config.CAMERA_DISTANCE_CAM_TABLE,
            alpha=self.config.CAMERA_CAM_OBJ_FUNCTION_A,
            beta=self.config.CAMERA_CAM_OBJ_FUNCTION_B,
        )
        camera.load_undistor_coefficients()

        ############################# PICKUP_ZONE DETECTION #############################
        camera.capture()
        camera.undistor_image()
        zones_plant = color_recognizer.detect(camera.get_capture())
        zones_plant = [zone for zone in zones_plant if (zone.bounding_box[1][0] - zone.bounding_box[0][0]) * (
                    zone.bounding_box[1][1] - zone.bounding_box[0][1]) > self.config.CAMERA_PICKUP_ZONE_MIN_AREA]
        if len(zones_plant) < 6:
            print("error in zone_plant detection")
        # calculate approximate center and exclude nearest cluster until there is 6 zones remaking
        elif len(zones_plant) > 6:
            mx = 0
            my = 0
            for z in zones_plant:
                mx += z.centroid[0]
                my += z.centroid[1]
            apro_center = Point(mx, my)
            zones_plant = sorted(zones_plant,
                                 key=lambda zone: apro_center.distance(Point(zone.centroid[0], zone.centroid[1])))
            while len(zones_plant) > 6:
                zones_plant.pop()

        for zone in zones_plant: print(zone.centroid)

        # ---Loop--- #
        camera.capture()
        camera.undistor_image()

        arucos = aruco_recognizer.detect(camera.get_capture())
        green_objects = color_recognizer.detect(camera.get_capture())

        arucos_tmp = []
        arucos_tmp.extend(
            (
                aruco.encoded_number,
                plan_transposer.image_to_relative_position(
                    img=camera.get_capture(),
                    segment=aruco.max_radius,
                    center_point=aruco.centroid,
                ),
            )
            for aruco in arucos
        )
        self.arucos = arucos_tmp

        green_objects_tmp = []
        green_objects_tmp.extend(
            green_object.centroid for green_object in green_objects
        )
        self.green_objects = green_objects_tmp

        frame = Frame(camera.get_capture(), [green_objects, arucos])
        frame.draw_markers()
        frame.write_labels()
        camera.update_monitor(frame.img)

    """ Main process routines """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def pami_com(self):
        """
        Send to pami all messages received from the websocket. (Essentially from ROB)
        -> It is this routine that will be used to send to the PAMI the start trigger.
        * This routine send the received message to everyone connected to the PAMI route.
        """
        message = await self.ws_pami.receiver.get()
        if message != WSmsg():
            self.logger.log(
                f"Message received on [PAMI]: {message}. Sending it to PAMIs.",
                LogLevels.DEBUG,
            )
            await self.ws_pami.sender.send(
                WSmsg(sender="server", msg=pami_state.msg, data=pami_state.data),
            )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def lidar_com(self):
        """
        Update the lidar points by listening to the LiDAR websocket (message from ROB).
        """
        message = await self.ws_lidar.receiver.get()
        if message != WSmsg():
            self.logger.log(f"Message received on [LiDAR]: {message.msg}.", LogLevels.DEBUG)
            self.lidar_points = [Point(x, y) for x, y in message.data]

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def odometer_com(self):
        """
        Update ROB position by listening to the odometer websocket (message from ROB).
        """
        message = await self.ws_odometer.receiver.get()
        if message != WSmsg():
            self.logger.log(
                f"Message received on [Odometer]: {message}.", LogLevels.DEBUG
            )
            self.rob_pos = OrientedPoint(
                message.data[0], message.data[1], message.data[2]
            )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def camera_com(self):
        """
        Send to all clients connected to the camera route the data captured by the camera.
        (Essentially the arucos and green objects detected)
        """
        # Send Arucos
        await self.ws_camera.sender.send(
            WSmsg(sender="server", msg="arucos", data=self.arucos)
        )
        # Send Green objects
        await self.ws_camera.sender.send(
            WSmsg(sender="server", msg="green_objects", data=self.green_objects)
        )

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
    async def display_lidar_points(self):
        def init():
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 10)
            return (self.ln,)

        def update(frame):
            points_list = self.lidar_points

            xdata = [point.x for point in points_list]
            ydata = [point.y for point in points_list]

            self.ln.set_data(xdata, ydata)
            return (self.ln,)

        ani = FuncAnimation(
            self.fig,
            update,
            frames=np.linspace(0, 2, 100),
            init_func=init,
            blit=True,
            interval=500,
        )

        plt.show(block=False)

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def main(self):
        """
        Main routine of the server brain.
        --> For the moment, it only sends the received command to ROB. (for zombie mode essentially)
        """
        cmd_state = await self.ws_cmd.receiver.get()
        # New cmd received !
        if cmd_state != WSmsg():
            self.logger.log(f"Message received on [CMD]: {cmd_state}.", LogLevels.INFO)

            if self.ws_cmd.get_client("rob") is not None:
                await self.ws_cmd.sender.send(
                    WSmsg(sender="server", msg=cmd_state.msg, data=cmd_state.data),
                    clients=self.ws_cmd.get_client("rob"),
                )
