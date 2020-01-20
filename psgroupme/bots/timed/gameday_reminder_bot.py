from recleagueparser.schedules import ScheduleFactory
from recleagueparser.rsvp_tools import RsvpToolFactory
from recleagueparser.player_stats import PlayerStatsFactory
from recleagueparser.team_stats import TeamStatsFactory
from psgroupme.database import PointstreakDatabase
from .base_timed_bot import BaseTimedBot
from .test_timed_bot import TestTimedBot
from time import sleep
import threading
import croniter
import datetime


class BaseGamedayReminderBot(BaseTimedBot):

    DEFAULT_STATS_TYPE = 'sportsengine'

    def __init__(self, **kwargs):
        super(BaseGamedayReminderBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.schedule_cfg = self.bot_data.get('schedule', dict())
        self.stats_cfg = self.bot_data.get('stats', self.schedule_cfg)
        self.rsvp_cfg = self.bot_data.get('rsvp')
        self.playoff_check = self.bot_data.get('playoff_check', False)
        self.schedule_type = self.schedule_cfg.get('type', 'pointstreak')
        self.rsvp = None
        self.load_rsvp()

    def load_rsvp(self):
        # Set up RsvpTool
        self._logger.debug("Loading RSVP Parser")
        if self.rsvp is not None:
            self._logger.debug("Already loaded.")
            return
        if self.rsvp_cfg:
            self._logger.info("No RSVP Parser Loaded yet, creating new one.")
            if 'username' in self.rsvp_cfg and 'password' in self.rsvp_cfg:
                rsvp_type = self.rsvp_cfg.get('type')
                self.rsvp_cfg.update(dict(rsvp_tool_type=rsvp_type))
                self.rsvp = RsvpToolFactory.create(**self.rsvp_cfg)

    def load_player_stats(self):
        self._logger.info("Loading Player Stats Parser")
        stats_type = self.stats_cfg.get('type', 'pointstreak')
        self.player_stats = PlayerStatsFactory.create(stats_type,
                                                      **self.stats_cfg)

    def load_team_stats(self):
        self._logger.info("Loading Team Stats Parser")
        stats_type = self.stats_cfg.get('type', 'pointstreak')
        self.team_stats = TeamStatsFactory.create(stats_type,
                                                  **self.stats_cfg)

    def get_playoff_danger_str(self):
        if self.playoff_check:
            self._logger.info("Playoff Warning Check: Enabled")
            self.load_player_stats()
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
                return "\r\n{0}".format(danger_str)
        return ''

    def send_game_notification(self, *args, **kwargs):
        raise NotImplementedError

    def _send_game_notification(self, game, days=0):
        game_str = "{0} vs {1} at {2}".format(game['hometeam'],
                                              game['awayteam'],
                                              game['time'])
        msg = ''
        if days > 0:
            days_str = 'tomorrow' if days == 1 else 'in {} days'.format(days)
            msg = "Game Reminder - There is a game {}: {}!".format(days_str,
                                                                   game_str)
        else:
            msg = "It's Gameday!"
            msg = "{0} {1}".format(msg, game_str)
            if self.rsvp is not None and days == 0:
                self.load_rsvp()
                self.rsvp.reset_game_data()
                attendance = self.rsvp.get_next_game_attendance()
                msg = "{0}\r\n{1}".format(msg, attendance)
            msg = '{}{}'.format(msg, self.get_playoff_danger_str())
        self._logger.debug("Generated Msg: {}".format(msg))
        self.send_msg(msg)
        sleep(1)

    def run(self):
        raise NotImplementedError


class CronGamedayReminderBot(BaseGamedayReminderBot):

    DEFAULT_CRON = "0 12 * * *"

    def __init__(self, *args, **kwargs):
        super(CronGamedayReminderBot, self).__init__(*args, **kwargs)
        self.debug = self.bot_data.get('debug')
        self.cron = self.bot_data.get('cron', self.DEFAULT_CRON)
        self.notify_days = self.bot_data.get('notify_days', 0)
        if not isinstance(self.notify_days, list):
            self.notify_days = [self.notify_days]
        self.notify_days = [int(x) for x in self.notify_days]

    def gametime_diff(self, from_date, to_date):
        return (to_date.replace(hour=0, minute=0) -
                from_date.replace(hour=0, minute=0)).days + 1

    def check_for_game_and_notify(self):
        try:
            self.sched = ScheduleFactory.create(self.schedule_type,
                                                **self.schedule_cfg)
            self.sched.refresh_schedule()
            self._logger.info("Checking Schedule for notifiable games...")
            now = datetime.datetime.utcnow()
            for game in reversed(self.sched.games):
                days_til_game = self.gametime_diff(now, game.full_gametime)
                if days_til_game in self.notify_days:
                    super(CronGamedayReminderBot,
                          self)._send_game_notification(game.data,
                                                        days=days_til_game)
        except Exception:
            self._logger.exception("Could Not Check Schedule")

    def run(self):
        self._logger.info("Starting {} Thread".format(self.__class__.__name__))
        while not self.stopped:
            now = datetime.datetime.utcnow()

            cron = croniter.croniter(self.cron, now)
            next_run = cron.get_next(datetime.datetime)
            if self.debug:
                next_run = now + datetime.timedelta(0, 2)
            delta = (next_run - now).total_seconds()
            self._logger.info("Next Run at: {}".format(next_run))
            t = threading.Timer(delta, self.check_for_game_and_notify)
            t.daemon = True
            t.start()
            while t.is_alive():
                sleep(1)


class DatabaseGamedayReminderBot(BaseGamedayReminderBot):

    MORNING_CUTOFF = datetime.time(10, 00)
    NIGHT_CUTOFF = datetime.time(22, 00)

    def ok_time_to_send_msg(self):
        self._logger.debug("Checking if now is within the notifiable window"
                           "of {} to {}".format(self.MORNING_CUTOFF,
                                                self.NIGHT_CUTOFF))
        now = datetime.datetime.now().time()
        return self.MORNING_CUTOFF <= now <= self.NIGHT_CUTOFF

    def game_has_been_notified(self, game_id):
        self._logger.debug("Checking if Game {} has been notified".format(
            game_id))
        return self.db.game_has_been_notified(game_id)

    def get_game(self, game_id):
        self._logger.debug("Retreiving Game {} from DB".format(game_id))
        return self.db.get_game(game_id)

    def run(self):
        # Set up Database
        # TODO: Can we move this inside run loop?
        self._logger.info("Setting up Pointstreak DB")
        self.db = PointstreakDatabase()
        self._logger.info("Setting up Schedule")
        self.sched = ScheduleFactory.create(self.schedule_type,
                                            **self.schedule_cfg)
        self.sched.refresh_schedule()
        self.db.load_schedule(self.sched)
        team_id = self.sched.team_id
        season_id = self.sched.season_id
        while True:
            if self.db.is_game_today(team_id, season_id):
                game_id = self.db.get_todays_game(team_id, season_id)
                self._check_and_notify_game(game_id)

    def _check_and_notify_game(self, game_id):
        if not self.game_has_been_notified(game_id) and \
                self.ok_time_to_send_msg():
            self._logger.info("OK to send notification")
            game = self.db.get_game(game_id)
            self._send_game_notification(game)
            self.db.set_notified(game_id, True)


class GamedayReminderBot(CronGamedayReminderBot, DatabaseGamedayReminderBot):

    def __init__(self, **kwargs):
        self.bot_data = kwargs
        if 'database' in self.bot_data:
            DatabaseGamedayReminderBot.__init__(self, **kwargs)
        else:
            CronGamedayReminderBot.__init__(self, **kwargs)


class TestGamedayReminderBot(TestTimedBot, GamedayReminderBot):
    pass
