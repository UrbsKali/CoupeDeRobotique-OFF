# Import from common
from logger import Logger, LogLevels

# External imports
from typing import TypeVar
import numpy as np
import math

TLidar = TypeVar("TLidar", bound="pysicktim")


class Lidar:
    """
    This class is a wrapper for the lidar sensor.
    * The angles are in degrees (considering the sense in the trigonometric way).
            -> 0° is the front of the robot
            -> 90° is the left of the robot
            -> -90° is the right of the robot
    * The distances are in centimeters.
    * the unities of angles and distances can be changed by changing the default values of the _init_ parameters.
    * The lidar is a SICK TIM 571.
    * The angle and distance are stored in a numpy array (type float32).
    """

    def __init__(self, logger: Logger, min_angle: float, max_angle: float, unity_angle: str = "deg",
                 unity_distance: str = "cm") -> None:
        """
        Initialize the lidar object and the polars angles.
        It also tests the lidar connection.

        WARNING: The min & max angle have to be given in the trigonometric way and in degrees !

        :param logger: logger to log the lidar's events
        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :param unity_angle: the unity of the angles (default: "deg")
        :param unity_distance: the unity of the distances (default: "cm")
        :return:
        """
        self._logger = logger
        self.__distance_unity = self.__init_distances_unity(unity_distance)
        self.__angle_unity = self.__init_angles_unity(unity_angle)

        self.__lidar_obj = self.__init_lidar()
        self.__polars_angles = self.__init_polars_angle(min_angle, max_angle)

    """
        Private methods
    """

    def __init_lidar(self) -> TLidar:
        """
        Initialize the lidar object and test the connection.
        :return: the lidar object
        """
        try:
            import pysicktim as lidar

            if lidar is None:
                self._logger.log("Lidar is not connected !", LogLevels.CRITICAL)
                raise ConnectionError("Lidar is not connected !")
            else:
                self._logger.log("Lidar is connected !", LogLevels.INFO)

            # Test lidar connection by testing scan function
            lidar.scan()
            if lidar.scan.distances is None or lidar.scan.distances == []:
                self._logger.log("Lidar doesn't work correctly", LogLevels.CRITICAL)
                raise ConnectionError("Lidar doesn't work correctly !")

            return lidar

        except ImportError as error:
            self._logger.log(f"Error while importing lidar [{error}]", LogLevels.CRITICAL)
            raise ImportError(f"Error while importing lidar [{error}] !")

    def __init_polars_angle(self, min_angle: float, max_angle: float) -> np.ndarray:
        """
        Initialize the polars angles array
        :param min_angle: the minimum angle of the lidar (max angle at left)
        :param max_angle: the maximum angle of the lidar (min angle at right)
        :return:
        """
        n = len(self.distances)  # Number of distances
        if n == 0:
            self.__scan()

        angle_step = abs(max_angle - min_angle) / n

        # Init the polars array with zeros, then fill it with angles
        polars = np.zeros(n, dtype=np.float32)
        for i in range(n):
            polars[i] = i * angle_step

        if polars.size == 0:
            self._logger.log("Error while initializing polars", LogLevels.CRITICAL)
            raise ValueError("Error while initializing polars !")

        return polars

    def __init_distances_unity(self, unity: str) -> float:
        """
        Initialize the unity of the distances
        :param unity_distance: the unity of the distances
        :return:
        """
        if unity == "mm":
            return 0.001
        if unity == "cm":
            return 0.01
        if unity == "m":
            return 1
        if unity == "inch":
            return 0.0254

        self._logger.log(f"Unity of distances not recognized [{unity}] !", LogLevels.CRITICAL)
        raise ValueError(f"Unity of distances not recognized [{unity}] !")

    def __init_angles_unity(self, unity: str) -> float:
        """
        Initialize the unity of the angles
        :param unity_angle: the unity of the angles
        :return:
        """
        if unity == "deg":
            return 1
        if unity == "rad":
            return 180 / math.pi

        self._logger.log(f"Unity of angles not recognized [{unity}] !", LogLevels.CRITICAL)
        raise ValueError(f"Unity of angles not recognized [{unity}] !")

    def __scan(self):
        """
        Scan the environment with the lidar and store the distances.
        in the lidar object.
        """
        self.__lidar_obj.scan()

    """
        Public methods and properties
    """

    @property
    def distances(self) -> np.ndarray:
        """
        Get the distances from the last scan.
        It automatically converts the distances to the right unity.
        :return: the distances array
        """
        return np.array(self.__lidar_obj.scan.distances, dtype=np.float32) * self.__distance_unity

    @property
    def polars(self) -> np.ndarray:
        """
        Get the polars array.
        It automatically converts the angles to the right unity.
        :return: the polars array
        """
        return np.concatenate((self.__polars_angles, self.distances), axis=1) * self.__angle_unity

    def scan_to_distances(self) -> np.ndarray:
        """
        Scan the environment with the lidar and return the distances.
        :return: the distances array
        """
        self.__scan()
        return self.distances

    def scan_to_polars(self) -> np.ndarray:
        """
        Scan the environment with the lidar and return the polars array.
        :return: the polars array
        """
        self.__scan()
        return self.polars
