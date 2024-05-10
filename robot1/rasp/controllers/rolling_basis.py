from config_loader import CONFIG

# Import from common
from teensy_comms import Teensy
from logger import Logger, LogLevels
from utils import Utils

import struct
import math
import asyncio
from enum import Enum
from dataclasses import dataclass
import time


class Command(Enum):
    VROOM = b"\x01"
    ROTATE = b"\x02"
    L_MOTOR = b"\x03"
    R_MOTOR = b"\x04"
    STOP = b"\x05"
    INVALID = b"\xFF"


@dataclass
class Instruction:
    cmd: Command
    msg: bytes  # msg is often the same as cmd, but can contain extra info

    def __str__(self):
        return f"cmd:{self.cmd}, msg:{self.msg}"




class Pipou(Teensy):
    ######################
    # Rolling basis init #
    ######################
    def __init__(
        self,
        logger: Logger,
        ser: int = CONFIG.ROLLING_BASIS_TEENSY_SER,
        crc: bool = CONFIG.TEENSY_CRC,
        vid: int = CONFIG.TEENSY_VID,
        pid: int = CONFIG.TEENSY_PID,
        baudrate: int = CONFIG.TEENSY_BAUDRATE,
        dummy: bool = CONFIG.TEENSY_DUMMY,
    ):
        super().__init__(
            logger, ser=ser, vid=vid, pid=pid, baudrate=baudrate, crc=crc, dummy=dummy
        )
        """
        This is used to match a handling function to a message type.
        add_callback can also be used.
        """
        self.messagetype = {
            130: self.rcv_print,  # \x82
            255: self.rcv_unknown_msg,
        }

    #############################
    # Received message handling #
    #############################
    def rcv_print(self, msg: bytes):
        self.logger.log(
            "Teensy says : " + msg.decode("ascii", errors="ignore"), LogLevels.INFO
        )

    def rcv_unknown_msg(self, msg: bytes):
        self.logger.log(
            f"Teensy does not know the command {msg.hex()}", LogLevels.WARNING
        )

   ##################
   # Messaging part #
   ##################
    def vromm(self, speed: int, direction: bool):
        """
        Send a vromm command to the Teensy.
        """
        msg = (
            Command.VROUM
            + struct.pack("<H", speed)
            + struct.pack("<?", direction)            
        )
        self.send_bytes(msg)
        
    def rotate(self, speed: int, direction: bool):
        """
        Send a rotate command to the Teensy.
        """
        msg = (
            Command.ROTATE
            + struct.pack("<H", speed)
            + struct.pack("<?", direction)            
        )
        self.send_bytes(msg)
        
    def l_motor(self, speed: int, direction: bool):
        """
        Control the left motor of the robot.
        """
        msg = (
            Command.L_MOTOR
            + struct.pack("<H", speed)
            + struct.pack("<?", direction)            
        )
        self.send_bytes(msg)
        
    def r_motor(self, speed: int, direction: bool):
        """
        Control the right motor of the robot.
        """
        msg = (
            Command.R_MOTOR
            + struct.pack("<H", speed)
            + struct.pack("<?", direction)            
        )
        self.send_bytes(msg)
        
    def stop(self):
        """
        Send a stop command to the Teensy.
        """
        msg = Command.STOP
        self.send_bytes(msg)