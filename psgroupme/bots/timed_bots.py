from database import PointstreakDatabase
from factories import ScheduleFactory, RsvpToolFactory, PlayerStatsFactory
from interfaces.responder import Responder
from time import sleep
import datetime
import threading
import logging


class TimedBot(threading.Thread):

    def __init__(self, **kwargs):
        """Load the config for this bot based on Name"""
        super(TimedBot, self).__init__()
        self._stop_event = threading.Event()
        self.daemon = True
        self.bot_id = kwargs.get('bot_id')
        assert self.bot_id is not None
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
    DEFAULT_STATS_TYPE = 'sportsengine'

    def __init__(self, **kwargs):
        super(GamedayReminderBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.schedule_type = kwargs.get('schedule_type', 'pointstreak')
        self.team_id = kwargs.get('team_id')
        self.season_id = kwargs.get('schedule_id', 0)
        self.company_id = kwargs.get('company_id', 'UnknownCompany')
        self.playoff_check = kwargs.get('playoff_check', False)
        self.rsvp = None
        self.load_rsvp()

    def load_rsvp(self):
        # Set up RsvpTool
        if self.rsvp is not None:
            return
        if 'rsvp_tool_type' in self.bot_data:
            self.rsvp_tool_type = self.bot_data.get('rsvp_tool_type', 'tlr')
            self.rsvp_username = self.bot_data.get('rsvp_username', None)
            self.rsvp_password = self.bot_data.get('rsvp_password', None)
            if self.rsvp_username is not None and self.rsvp_password is \
                    not None:
                rsvp_kwargs = dict(username=self.rsvp_username,
                                   password=self.rsvp_password)
                self.rsvp = RsvpToolFactory.create(self.rsvp_tool_type,
                                                   **rsvp_kwargs)

    def load_stats(self):
        self.stats_type = self.bot_data.get(
            'stats_type',
            self.bot_data.get('schedule_type', self.DEFAULT_STATS_TYPE)
        )
        stats_kwargs = dict(team_id=self.team_id, season_id=self.season_id)
        self.player_stats = PlayerStatsFactory.create(self.stats_type,
                                                      **stats_kwargs)

    def game_has_been_notified(self, game_id):
        return self.db.game_has_been_notified(game_id)

    def send_game_notification(self, game_id):
        game = self.db.get_game(game_id)
        msg = "Its Gameday! {0} vs {1} at {2}".format(game['hometeam'],
                                                      game['awayteam'],
                                                      game['time'])
        if self.rsvp is not None:
            self.load_rsvp()
            msg = "{0}\r\n{1}".format(msg,
                                      self.rsvp.get_next_game_attendance())
        if self.playoff_check:
            self.load_stats()
            sched_length = self.sched.length
            games_remaining = self.sched.games_remaining
            danger_str = 'Playoff elligibility:'
            danger_exists = False
            for player in self.player_stats.get_playoff_danger(
                    sched_length, games_remaining):
                danger_exists = True
                missable = player.get_missable_games(sched_length,
                                                     games_remaining)
                danger_str += '\r\n{0} can only miss {1} more games'.format(
                   player.name, missable)
            if danger_exists:
                msg = "{0}\r\n{1}".format(msg, danger_str)
        logging.info(msg)
        self.send_msg(msg)
        self.db.set_notified(game_id, True)
        sleep(1)

    def ok_time_to_send_msg(self):
        now = datetime.datetime.now().time()
        return self.MORNING_CUTOFF <= now <= self.NIGHT_CUTOFF

    def run(self):
        # Set up Database
        sched_kwargs = dict(team_id=self.team_id, season_id=self.season_id,
                            company=self.company_id)
        self.db = PointstreakDatabase()
        self.sched = ScheduleFactory.create(self.schedule_type, **sched_kwargs)
        self.sched.refresh_schedule()
        self.db.load_schedule(self.sched)
        self.team_id = self.sched.team_id
        self.season_id = self.sched.season_id
        while True:
            if self.db.is_game_today(self.team_id, self.season_id):
                game_id = self.db.get_todays_game(self.team_id, self.season_id)
                if not self.game_has_been_notified(game_id) and \
                        self.ok_time_to_send_msg():
                    self.send_game_notification(game_id)


class TestGamedayReminderBot(GamedayReminderBot):

    def send_msg(self, msg):
        print(msg)


def main():
    grb = GamedayReminderBot()
    grb.run()


if __name__ == '__main__':
    main()
