from .base_timed_bot import BaseTimedBot
from time import sleep

class TimedPingBot(BaseTimedBot):

    DEFAULT_SLEEP = 5

    def __init__(self, sleep=DEFAULT_SLEEP, **kwargs):
        super(TimedPingBot, self).__init__(**kwargs)
        self.sleep = sleep

    def run(self):
        while not self.stopped:
            self.send_msg("ping")
            sleep(self.sleep)
