# External imports
# ...

# Import from common
from brain import Brain

from logger import Logger, LogLevels
from geometry import OrientedPoint, Point
from WS_comms import WSmsg


# Import from local path
# ...


@Brain.task(process=False, run_on_start=True, refresh_rate=0.5)
async def odometer_com(self):
    """
    Update ROB position by listening to the odometer websocket (message from ROB).
    """
    message = await self.ws_odometer.receiver.get()
    if message != WSmsg():
        self.logger.log(f"Message received on [Odometer]: {message}.", LogLevels.DEBUG)
        self.rob_pos = OrientedPoint(message.data[0], message.data[1], message.data[2])

        if self.ws_odometer.get_client("WebUI") is not None:
            await self.ws_odometer.sender.send(
                WSmsg(sender="server", msg=message.msg, data=message.data),
                clients=self.ws_odometer.get_client("WebUI"),
            )
