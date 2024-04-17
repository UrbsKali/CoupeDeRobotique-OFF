from enum import Enum


class AntiCollisionMode(Enum):
    DISABLED = 0  # No anti-collision not implemented
    CIRCULAR = 1  # Stop when an obstacle is detected not implemented
    FRONTAL = (
        3  # Stop when an obstacle is detected in front of the robot not implemented
    )


class AntiCollisionHandle(Enum):
    CHANGE_DIRECTION = (
        0  # Change direction when an obstacle is detected not implemented
    )
    AVOID = 1  # Avoid the obstacle not implemented
