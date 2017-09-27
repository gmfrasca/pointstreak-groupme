from database import PointstreakDatabase
from config_manager import ConfigManager
from team_schedule import PointstreakSchedule
from responder import Responder
from time import sleep
import threading


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
        print "\nStopping Bot {0}".format(self.bot_type)
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def send_msg(self, msg):
        self.responder.reply(msg)


class GamedayReminderBot(TimedBot):

    def run(self):
        # Set up Database
        self.db = PointstreakDatabase()
        self.sched = PointstreakSchedule()
        self.db.load_schedule(self.sched)
        self.team_id = self.sched.team_id
        self.season_id = self.sched.season_id

        while True:
            if self.db.is_game_today(self.team_id, self.season_id):
                game_id = self.db.get_todays_game(self.team_id, self.season_id)
                if not self.game_has_been_notified(game_id):
                    print("Game Today")
                    sleep(60)
