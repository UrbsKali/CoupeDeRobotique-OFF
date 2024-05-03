from enum import Enum


class AntiCollisionMode(Enum):
    # No anti-collision not implemented
    DISABLED = 0
    # Stop when an obstacle is detected not implemented
    CIRCULAR = 1
    # Stop when an obstacle is detected in front of the robot not implemented
    FRONTAL = 2


class AntiCollisionHandle(Enum):

    NOTHING = 0
    WAIT_AND_FAIL = 1
    WAIT_AND_RETRY = 2
    AVOID = 3  # Not implemented
