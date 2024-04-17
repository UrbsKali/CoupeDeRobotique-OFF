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
        ServoGoTo = b"\x01"
        StepperStep = b"\x02"

    def __str__(self) -> str:
        return self.__class__.__name__

    #########################
    # User facing functions #
    #########################

    @Logger
    def stepper_step(
        self, steps: int, number_of_steps: int, motor_pin_1: int, motor_pin_2: int, motor_pin_3: int, motor_pin_4: int
    ) -> None:
        """
        Moves the stepper motor a specified number of steps. Note that the number of motor pin can change depending on the motor.
        2 or 5 pins are common.

        Args:
            steps (int): The number of steps to move the motor.
            number_of_steps (int): The total number of steps the motor can take in one revolution.
            motor_pin_1 (int): The pin number for motor pin 1.
            motor_pin_2 (int): The pin number for motor pin 2.
            motor_pin_3 (int): The pin number for motor pin 3.
            motor_pin_4 (int): The pin number for motor pin 4.

        Returns:
            None
        """
        msg = (
            self.Command.StepperStep
            + struct.pack("<b", steps)
            + struct.pack("<B", number_of_steps)
            + struct.pack("<B", motor_pin_1)
            + struct.pack("<B", motor_pin_2)
            + struct.pack("<B", motor_pin_3)
            + struct.pack("<B", motor_pin_4)
            # https://docs.python.org/3/library/struct.html#format-characters
        )
        self.send_bytes(msg)
        

    @Logger
    def update_servo(
        self, pin: int, angle: int, min_angle: int = 0, max_angle: int = 180
    )->None:
        """set angle to the servo at the given pin

        Args:
            pin (int): servo's pin
            angle (int): the angle to set
            min_angle (int, optional): angle lower -> angle won't be set. Defaults to 0.
            max_angle (int, optional): angle higher -> angle won't be set. Defaults to 180.
        """
        if angle >= min_angle and angle <= max_angle:
            msg = (
                self.Command.ServoGoTo
                + struct.pack("<B", pin)
                + struct.pack("<B", angle)
            )
            # https://docs.python.org/3/library/struct.html#format-characters
            self.send_bytes(msg)
        else:
            self.l.log(
                f"you tried to write {angle}° on pin {pin} whereas angle must be between {min_angle} and {max_angle}°",
                LogLevels.ERROR,
            )
