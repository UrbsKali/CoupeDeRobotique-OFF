from rpi_ws281x import PixelStrip, Color
from logger.log_tools import LogLevels
from logger.logger import Logger

LogColors = {
    LogLevels.DEBUG: Color(0, 0, 255),
    LogLevels.INFO: Color(0, 0, 255),
    LogLevels.WARNING: Color(250, 250, 0),
    LogLevels.ERROR: Color(255, 0, 0),
    LogLevels.CRITICAL: Color(255, 0, 0),
    LogLevels.FATAL: Color(255, 0, 0),
}


class Colors:
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    ORANGE = Color(255, 165, 0)
    PINK = Color(255, 192, 203)
    PURPLE = Color(128, 0, 128)
    BROWN = Color(165, 42, 42)


class LEDStrip:
    def __init__(self, num_leds, pin, frequency, brightness, led_indexes):
        self._strip = PixelStrip(
            num=num_leds, pin=pin, freq_hz=frequency, brightness=brightness
        )
        self._strip.begin()
        self.set_color(Color(0, 0, 0))
        self.led_indexes = led_indexes

        self.is_ready(False)
        self.set_jack(False)

        self.log_history = [Colors.BLACK for _ in range(self.led_indexes["log"])]

    def set_color(self, color: Color | list[Color], index: list | int | None = None):
        if index is None and isinstance(color, Color):
            for i in range(self._strip.numPixels()):
                self._strip.setPixelColor(i, color)
        if isinstance(index, int) and isinstance(color, Color):
            self._strip.setPixelColor(index, color)
        if (
            isinstance(index, list)
            and isinstance(color, list)
            and len(index) == len(color)
        ):
            for i in index:
                self._strip.setPixelColor(i, color[i])
        if isinstance(index, list) and isinstance(color, Color):
            for i in index:
                self._strip.setPixelColor(i, color)
        self._strip.show()

    def set_color_range(self, start, end, color):
        for i in range(start, end):
            self._strip.setPixelColor(i, color)
        self._strip.show()

    def set_color_single(self, index, color):
        self._strip.setPixelColor(index, color)
        self._strip.show()

    def clear(self):
        self.set_color(Color(0, 0, 0))

    def log(self, log_level: LogLevels):
        self.log_history.insert(0, LogColors[log_level])
        self.log_history[-1].pop()
        self.set_color(self.log_history, self.led_indexes["log"])

    def is_ready(self, state=True):
        self.set_color(
            Colors.GREEN if state else Colors.RED,
            self.led_indexes["is_ready"],
        )

    def set_jack(self, state):
        self.set_color(Colors.GREEN if state else Colors.RED, self.led_indexes["jack"])

    def set_team(self, team):
        self.set_color(
            Colors.YELLOW if team == "y" else Colors.BLUE, self.led_indexes["team"]
        )

    def acs_state(self, state):
        self.set_color(Colors.RED if state else Colors.GREEN, self.led_indexes["acs"])

    def set_progress(self, total_duration, current_progress):
        progress = int(
            (current_progress / total_duration) * len(self.led_indexes["progress"])
        )
        self.set_color(Colors.ORANGE, self.led_indexes["progress"][:progress])
        self.set_color(Colors.BLACK, self.led_indexes["progress"][progress:])
