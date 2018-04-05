from database import PointstreakDatabase
from config_manager import ConfigManager
from factories import ScheduleFactory
from interfaces.responder import Responder
from time import sleep
import datetime
import threading
import logging


class TimedBot(threading.Thread):

    def __init__(self, cfg_path=None):
        """Load the config for this bot based on Name"""
        super(TimedBot, self).__init__()
        self._stop_event = threading.Event()
        self.daemon = True

        # Get the Bot Config
        self.cfg_mgr = ConfigManager(cfg_path)
        self.bot_data = self.cfg_mgr.get_bot_data(self.bot_type)
        self.bot_id = self.cfg_mgr.get_bot_id(self.bot_type)
        self.bot_id = self.bot_data.get('bot_id')
        self.bot_name = self.bot_data.get('bot_name', 'UnknownBot')
        self.group_id = self.bot_data.get('group_id', 'UnknownGroup')
        self.group_name = self.bot_data.get('group_name', 'UnknownGroup')
        self.callback_url = self.bot_data.get('callback_url', None)
        self.avatar_url = self.bot_data.get('avatar_url', None)
        assert self.bot_id is not None

        # Set up the Responder
        self.responder = Responder(self.bot_id)

    @property
    def bot_type(self):
        return type(self).__name__

    def run(self):
        # Override This
        return True

    def stop(self):
        logging.info("Stopping Bot {0}".format(self.bot_type))
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def send_msg(self, msg):
        self.responder.reply(msg)


class GamedayReminderBot(TimedBot):

    MORNING_CUTOFF = datetime.time(10, 00)
    NIGHT_CUTOFF = datetime.time(22, 00)

    def game_has_been_notified(self, game_id):
        return self.db.game_has_been_notified(game_id)

    def send_game_notification(self, game_id):
        game = self.db.get_game(game_id)
        msg = "Its Gameday! {0} vs {1} at {2}".format(game['hometeam'],
                                                      game['awayteam'],
                                                      game['time'])
        logging.info(msg)
        self.send_msg(msg)
        self.db.set_notified(game_id, True)
        sleep(1)

    def ok_time_to_send_msg(self):
        now = datetime.datetime.now().time()
        return self.MORNING_CUTOFF <= now <= self.NIGHT_CUTOFF

    def run(self):
        # Set up Database
        self.db = PointstreakDatabase()
        self.sched = ScheduleFactory.create('pointstreak')
        self.db.load_schedule(self.sched)
        self.team_id = self.sched.team_id
        self.season_id = self.sched.season_id

        while True:
            if self.db.is_game_today(self.team_id, self.season_id):
                game_id = self.db.get_todays_game(self.team_id, self.season_id)
                if not self.game_has_been_notified(game_id) and \
                        self.ok_time_to_send_msg():
                    self.send_game_notification(game_id)


def main():
    grb = GamedayReminderBot()
    grb.run()


if __name__ == '__main__':
    main()
