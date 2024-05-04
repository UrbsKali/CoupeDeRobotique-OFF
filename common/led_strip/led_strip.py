from rpi_ws281x import PixelStrip, Color
from logger.log_tools import LogLevels

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
    def __init__(self, num_leds, pin, freq, brightness):
        self._strip = PixelStrip(
            num=num_leds, pin=pin, freq_hz=freq, brightness=brightness
        )
        self._strip.begin()
        self.set_color(Color(0, 0, 0))

        self.is_ready(False)
        self.set_jack(False)

    def set_color(self, color):
        for i in range(self._strip.numPixels()):
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

    def new_log(self, log_level: LogLevels):
        self.set_color_single(0, LogColors[log_level])

    def is_ready(self, state=True):
        self.set_color_single(1, Colors.GREEN if state else Colors.RED)

    def set_jack(self, state):
        self.set_color_single(2, Colors.GREEN if state else Colors.RED)

    def set_team(self, team):
        self.set_color_single(3, Colors.YELLOW if team == "y" else Colors.BLUE)

    def acs_state(self, state):
        self.set_color_single(4, Colors.RED if state else Colors.GREEN)

    def set_progress(self, total_duration, current_progress):
        progress = int((current_progress / total_duration) * self._strip.numPixels())
        self.set_color_range(5, 5 + progress, Colors.ORANGE)
        self.set_color_range(5 + progress, self._strip.numPixels(), Colors.BLACK)
