from enum import Enum


class AntiCollisionMode(Enum):
    # No anti-collision not implemented
    DISABLED = 0
    # Stop when an obstacle is detected not implemented
    CIRCULAR = 1
    # Stop when an obstacle is detected in front of the robot not implemented
    FRONTAL = 2


class AntiCollisionHandle(Enum):
    # Change direction when an obstacle is detected not implemented
    CHANGE_DIRECTION = 0
    # Avoid the obstacle not implemented
    AVOID = 1
