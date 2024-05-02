from config_loader import CONFIG
from logger import Logger, LogLevels
from arena import MarsArena
from geometry import Point

import matplotlib.pyplot as plt
from geometry import Point
from random import randint
from matplotlib.patches import Polygon as PolygonPatch


def test_enable_go_to():
    # Assuming CONFIG, Logger, MarsArena, and other necessary imports are present

    logger = Logger()
    arena = MarsArena(1, logger, border_buffer=CONFIG.ARENA_CONFIG["border_buffer"], robot_buffer=CONFIG.ARENA_CONFIG["robot_buffer"])

    # Display the required points in the graph
    x_start = []
    y_start = []
    x_stop = []
    y_stop = []
    for i in range(100):
        start = Point(randint(0, 200), randint(0, 300))
        stop = Point(randint(0, 200), randint(0, 300))
        if not arena.enable_go_to_point(start, stop):
            x_start.append(start.x)
            y_start.append(start.y)
            x_stop.append(stop.x)
            y_stop.append(stop.y)
            plt.plot([start.y, stop.y], [start.x, stop.x], color="black")

    # Display forbidden zone polygon
    forbidden_zone = arena.zones["forbidden"]
    if forbidden_zone:
        # Extract the coordinates of the exterior boundary
        xy = forbidden_zone.exterior.coords.xy
        xy = list(zip(xy[1], xy[0]))
        patch = PolygonPatch(xy, facecolor="red", edgecolor="red", alpha=0.5, zorder=2)
        plt.gca().add_patch(patch)

    # Set plot limits
    plt.xlim(0, 300)
    plt.ylim(200, 0)

    # Plot start and stop points
    plt.scatter(y_start, x_start, color="blue", label="Start")
    plt.scatter(y_stop, x_stop, color="red", label="Stop")

    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title("Disallowed Go-To")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    test_enable_go_to()
