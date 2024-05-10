# External imports
import asyncio
import time

# Import from common
from brain import Brain

from WS_comms import WSmsg, WServerRouteManager
from geometry import OrientedPoint, Point
from logger import Logger, LogLevels
from arena import MarsArena

# Import from local path
# ...


class MainBrain(Brain):
    """
    This brain is the main controller of the server.
    """

    def __init__(
        self,
        logger: Logger,
        ws_cmd: WServerRouteManager,
        config,
    ) -> None:

        # Init the brain
        super().__init__(logger, self)

    """
        Tasks
    """

    @Brain.task(process=False, run_on_start=True, refresh_rate=0.1)
    async def main(self):
        """
        Main routine of the server brain.
        --> For the moment, it only sends the received command to ROB. (for zombie mode essentially)
        """
        cmd_state = await self.ws_cmd.receiver.get()
        # New cmd received !
        if cmd_state != WSmsg():
            self.logger.log(f"Message received on [CMD]: {cmd_state}.", LogLevels.INFO)

            if self.ws_cmd.get_client("rob") is not None:
                await self.ws_cmd.sender.send(
                    WSmsg(sender="server", msg=cmd_state.msg, data=cmd_state.data),
                    clients=self.ws_cmd.get_client("rob"),
                )
