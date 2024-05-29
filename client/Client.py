import websockets as ws
from pydualsense import *
from enum import Enum
import asyncio


class ControlMode(Enum):
    Manual = 0
    Auto = 1


class Client:
    def __init__(
        self,
        control_mod=ControlMode.Manual,
        websocket_url="rob.local",
        websocket_port=8080,
        name="dualsens",
        deadzone=5,
        dummy_ws=False,
    ):
        self.name = name
        self.websocket_url = websocket_url
        self.websocket_port = websocket_port

        self.websocket = None
        self.controller = None

        self.control_mod = control_mod
        self.deadzone = deadzone
        self.dummy_ws = dummy_ws

        # Manual control
        self.throttle_l = 0
        self.throttle_r = 0
        self.reverse_l = False
        self.reverse_r = False

        # Auto control
        self.throttle = 0
        self.steering = 0
        self.reverse = False

        self.run = True

    async def start(self):
        if not self.dummy_ws:
            self.websocket = await ws.connect(
                f"ws://{self.websocket_url}:{self.websocket_port}/cmd?sender={self.name}"
            )
        self.controller = pydualsense()
        self.controller.init()
        while self.controller.states is None:
            await asyncio.sleep(0.1)
        self.controller.light.setPlayerID(PlayerID.PLAYER_3)
        if self.control_mod == ControlMode.Manual:
            self.controller.light.setColorI(255, 0, 0)
        else:
            self.controller.light.setColorI(10, 10, 235)

        self.controller.dpad_down += self.dpad_down_handler
        self.controller.circle_pressed += self.o_handler
        self.controller.cross_pressed += self.x_handler
        self.controller.l2_changed += self.l2_handler
        self.controller.r2_changed += self.r2_handler
        self.controller.left_joystick_changed += self.joystick_handler
        self.controller.share_pressed += self.share_handler
        while self.run:
            if self.control_mod == ControlMode.Manual:
                await self.manual_handler()
            else:
                await self.auto_handler()
            await asyncio.sleep(0.1)

    async def send_data(self, data):
        dat = (
            '{ "data": "'
            + data
            + '", "msg" : "eval", "sender" : "Dualsens", "ts":"12334"}'
        )
        if not self.dummy_ws:
            await self.websocket.send(dat)

    def stop(self):
        self.run = False
        self.controller.close()
        self.websocket = None

    async def manual_handler(self):
        if self.throttle_l > 0:
            await self.send_data(
                f"self.robot.l_motor({self.throttle_l}, {self.reverse_l})"
            )
            print("l_throttle: ", self.throttle_l, " - reverse: ", self.reverse_l)
        else:
            await self.send_data(
                f"self.robot.l_motor({0}, {True})"
            )

        if self.throttle_r > 0:
            await self.send_data(
                f"self.robot.r_motor({self.throttle_r}, {self.reverse_r})"
            )
            print("r_throttle: ", self.throttle_r, " - reverse: ", self.reverse_r)
        else:
            await self.send_data(
                f"self.robot.r_motor({0}, {True})"
            )

    async def auto_handler(self):
        l_force = self.throttle + self.steering
        r_force = self.throttle - self.steering

        if self.reverse:
            l_force = -l_force
            r_force = -r_force

        l_reverse = l_force < 0 
        r_reverse = r_force < 0
        if l_reverse:
            l_force = -l_force
        if r_reverse:
            r_force = -r_force

        if l_force > 255:
            l_force = 255
        if r_force > 255:
            r_force = 255

        print("l_force: ", l_force, " - l_reverse: ", l_reverse)
        print("r_force: ", r_force, " - r_reverse: ", r_reverse)

        await self.send_data(f"self.robot.l_motor({l_force}, {l_reverse})")
        await self.send_data(f"self.robot.r_motor({r_force}, {r_reverse})")

    def joystick_handler(self, stateX, stateY):
        self.steering = stateX
        self.reverse = stateY < 0

    def o_handler(self, state):
        if state == 1:
            self.stop()

    def x_handler(self, state):
        if state == 1:
            self.reverse_r = True
        else:
            self.reverse_r = False

    def dpad_down_handler(self, state):
        if state == 1:
            self.reverse_l = True
            self.reverse = True
        else:
            self.reverse_l = False
            self.reverse = False

    def l2_handler(self, state):
        if state > self.deadzone:
            self.throttle_l = state
        else:
            self.throttle_l = 0

    def r2_handler(self, state):
        if state < self.deadzone:
            self.throttle_r = 0
            self.throttle = 0
            return
        if self.control_mod == ControlMode.Manual:
            self.throttle_r = state
        else:
            self.throttle = state

    def share_handler(self, state):
        if state == 1:
            if self.control_mod == ControlMode.Manual:
                self.control_mod = ControlMode.Auto
                self.controller.light.setColorI(10, 10, 235)
            else:
                self.control_mod = ControlMode.Manual
                self.controller.light.setColorI(255, 0, 0)
