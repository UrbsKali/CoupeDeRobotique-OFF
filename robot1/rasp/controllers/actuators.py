from config_loader import CONFIG
from logger import Logger, LogLevels

# Import from common
from teensy_comms import Teensy

import struct


class Actuators(Teensy):
    def __init__(
        self,
        logger: Logger,
        ser=CONFIG.ACTUATOR_TEENSY_SER,
        vid=CONFIG.TEENSY_VID,
        pid=CONFIG.TEENSY_PID,
        crc=CONFIG.TEENSY_CRC,
        baudrate=CONFIG.TEENSY_BAUDRATE,
        dummy: bool = CONFIG.TEENSY_DUMMY,
    ):
        super().__init__(
            logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy
        )

    class Command:  # values must correspond to the one defined on the teensy
        Update_servo = b"\x01"
        StepperStep = b"\x02"
        Update_servo_detach = b"\x03"

    def __str__(self) -> str:
        return self.__class__.__name__

    #########################
    # User facing functions #
    #########################

    @Logger
    def stepper_step(self, steps: int, dir : bool, pin_dir: int, pin_step: int) -> None:
        """
        Moves the stepper motor a specified number of steps. Note that the number of motor pin can change depending on the motor.
        2 or 5 pins are common.

        Args:
            steps (int): The number of steps to move the motor.
            dir (bool): The direction of the motor.
            pin_dir (int): The pin number of the direction pin.
            pin_step (int): The pin number of the step pin.

        Returns:
            None
        """
        msg = (
            self.Command.StepperStep
            + struct.pack("<i", steps)
            + struct.pack("<?", dir)
            + struct.pack("<B", pin_dir)
            + struct.pack("<B", pin_step)
            # https://docs.python.org/3/library/struct.html#format-characters
        )
        self.send_bytes(msg)

    @Logger
    def update_servo(
        self,
        pin: int,
        angle: int,
        min_angle: int = 0,
        max_angle: int = 180,
        detach=False,  # If True, the servo will detach after setting the angle, DO NOT USE DETACH = TRUE AND DETACH = FALSE ON THE SAME SERVO
        detach_delay=1000,
    ) -> None:
        """Set the angle of the servo at the given pin.

        Args:
            pin (int): The pin number of the servo.
            angle (int): The angle to set for the servo.
            min_angle (int, optional): The minimum angle allowed for the servo. Defaults to 0.
            max_angle (int, optional): The maximum angle allowed for the servo. Defaults to 180.
            detach (bool, optional): Whether to detach the servo after setting the angle. Defaults to False.
            detach_delay (int, optional): The time in milliseconds to keep the servo detached. Defaults to 1000.
        """
        if angle >= min_angle and angle <= max_angle:
            if detach:
                msg = (
                    self.Command.Update_servo_detach
                    + struct.pack("<B", pin)
                    + struct.pack("<B", angle)
                    + struct.pack("<i", detach_delay)
                )
            else:
                msg = (
                    self.Command.Update_servo
                    + struct.pack("<B", pin)
                    + struct.pack("<B", angle)
                )
            # https://docs.python.org/3/library/struct.html#format-characters
            self.send_bytes(msg)
        else:
            self.logger.log(
                f"You tried to write {angle}° on pin {pin}, whereas the angle must be between {min_angle} and {max_angle}°",
                LogLevels.ERROR,
            )
