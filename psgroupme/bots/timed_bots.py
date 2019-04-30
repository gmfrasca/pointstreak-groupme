from factories import ScheduleFactory, RsvpToolFactory, PlayerStatsFactory
from factories import FinanceToolFactory, TeamStatsFactory
from interfaces.responder import Responder
from database import PointstreakDatabase
from util import parsetime as pt
from time import sleep
import datetime
import threading
import logging
import croniter


class TimedBot(threading.Thread):

    def __init__(self, **kwargs):
        """Load the config for this bot based on Name"""
        super(TimedBot, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
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
        self._logger.info("Stopping Bot {0}".format(self.bot_type))
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def send_msg(self, msg):
        if msg and msg != '':
            self.responder.reply(msg)


class TeamFeeReminderBot(TimedBot):

    DEFAULT_CRON = "0 12 * * 0"

    def __init__(self, **kwargs):
        super(TeamFeeReminderBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.finance_cfg = self.bot_data.get('finance')
        self.schedule = self.finance_cfg.get('schedule', self.DEFAULT_CRON)

    @property
    def season_start_date(self):
        start_date = self.finance_cfg.get('season_start')
        if start_date:
            date = pt.normalize_date(start_date, return_type=datetime.datetime)
            return date.replace(minute=0, hour=0, second=0, microsecond=0)
        return None

    def get_finance_tool(self):
        # Set up RsvpTool
        finance_cfg = self.finance_cfg.copy()
        if finance_cfg:
            if 'username' in finance_cfg and 'password' in finance_cfg:
                finance_type = finance_cfg.get('type')
                finance_cfg.update(dict(finance_tool_type=finance_type))
                return FinanceToolFactory.create(**finance_cfg)
        return None

    def post_msg(self):
        finance_tool = self.get_finance_tool()
        fee, paid, percent = finance_tool.get_team_fee_stats()
        # Run only if fee isn't fully paid
        if fee != paid:
            prog_bar = finance_tool.get_team_fee_progress()
            msg = ''
            if self.season_start_date:
                midnight = datetime.datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
                days = (self.season_start_date - midnight).days
                msg += 'The season starts today'
                if days < 0:
                    msg = 'The season started {} days ago'.format(-days)
                if days > 0:
                    msg = 'The season starts in {} days'.format(days)
                msg += ' and the team fee is not yet paid in full!\r\n\r\n'
            msg = "{}Current Team Fee Progress:\r\n{}".format(msg, prog_bar)
            self.send_msg(msg)

    def run(self):
        while not self.stopped:
            now = datetime.datetime.utcnow()
            cron = croniter.croniter(self.schedule, now)
            next_run = cron.get_next(datetime.datetime)
            delta = next_run - now
            t = threading.Timer(delta.total_seconds(), self.post_msg)
            t.daemon = True
            t.start()
            while t.is_alive():
                sleep(1)


class BaseGamedayReminderBot(TimedBot):

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
        if self.rsvp is not None:
            return
        if self.rsvp_cfg:
            if 'username' in self.rsvp_cfg and 'password' in self.rsvp_cfg:
                rsvp_type = self.rsvp_cfg.get('type')
                self.rsvp_cfg.update(dict(rsvp_tool_type=rsvp_type))
                self.rsvp = RsvpToolFactory.create(**self.rsvp_cfg)

    def load_player_stats(self):
        stats_type = self.stats_cfg.get('type', 'pointstreak')
        self.player_stats = PlayerStatsFactory.create(stats_type,
                                                      **self.stats_cfg)

    def load_team_stats(self):
        stats_type = self.stats_cfg.get('type', 'pointstreak')
        self.team_stats = TeamStatsFactory.create(stats_type,
                                                  **self.stats_cfg)

    def get_playoff_danger_str(self):
        if self.playoff_check:
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
                attendance = self.rsvp.get_next_game_attendance()
                msg = "{0}\r\n{1}".format(msg, attendance)
            msg = '{}{}'.format(msg, self.get_playoff_danger_str())
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
        while not self.stopped:
            now = datetime.datetime.utcnow()

            cron = croniter.croniter(self.cron, now)
            next_run = cron.get_next(datetime.datetime)
            if self.debug:
                next_run = now + datetime.timedelta(0, 2)
            delta = (next_run - now).total_seconds()
            t = threading.Timer(delta, self.check_for_game_and_notify)
            t.daemon = True
            t.start()
            while t.is_alive():
                sleep(1)


class DatabaseGamedayReminderBot(BaseGamedayReminderBot):

    MORNING_CUTOFF = datetime.time(10, 00)
    NIGHT_CUTOFF = datetime.time(22, 00)

    def ok_time_to_send_msg(self):
        now = datetime.datetime.now().time()
        return self.MORNING_CUTOFF <= now <= self.NIGHT_CUTOFF

    def game_has_been_notified(self, game_id):
        return self.db.game_has_been_notified(game_id)

    def get_game(self, game_id):
        return self.db.get_game(game_id)

    def run(self):
        # Set up Database
        # TODO: Can we move this inside run loop?
        self.db = PointstreakDatabase()
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


class UpdatedGameNotifierBot(TimedBot):
    def __init__(self, **kwargs):
        super(UpdatedGameNotifierBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.schedule_cfg = self.bot_data.get('schedule', dict())
        self.sleep_time = self.schedule_cfg.get('sleep_time', 600)
        self.schedule_type = self.schedule_cfg.get('type', 'pointstreak')
        self.result_responses = self.bot_data.get('result_responses', dict())

        self.sched = None
        self._init_schedule()

    def _init_schedule(self):
        while self.sched is None:
            try:
                self.sched = ScheduleFactory.create(self.schedule_type,
                                                    **self.schedule_cfg)
            except Exception:
                self._logger.error("Could not load schedule, "
                                   "retrying in 1 Minute.")
                sleep(1)

    def store_old_games(self):
        self.old_games = list()
        for game in self.sched.games:
            self.old_games.append(game.data)

    def refresh_schedule(self):
        try:
            self.store_old_games()
            self.sched.refresh_schedule()
        except Exception:
            self._logger.warning("Could not refresh schedule")

    def scores_are_different(self, old_dict, new_game):
        return (old_dict['homescore'] != new_game.homescore or
                old_dict['awayscore'] != new_game.awayscore)

    def game_finality_is_different(self, old_dict, new_game):
        return old_dict['final'] != new_game.final

    def time_is_different(self, old_dict, new_game):
        return old_dict['full_gametime_str'] != new_game.full_gametime_str

    def check_and_notify_schedule_changes(self):
        # TODO: Determine *WHICH* games were added or deleted
        # TODO: Check that game ids all match instead of assuming based on len
        self._logger.info("Checking for changes in schedule...")
        if len(self.old_games) < len(self.sched.games):
            self.send_msg("Schedule Change Detected: New Games Added!")
        elif len(self.old_games) > len(self.sched.games):
            self.send_msg("Schedule Change Detected: Games Removed!")
        else:
            msg = ''
            result_res = ''
            for x in range(0, len(self.old_games)):
                old = self.old_games[x]
                new = self.sched.games[x]
                if self.game_finality_is_different(old, new):
                    msg += "Final Score:\r\n{}\r\n".format(new)
                    if isinstance(self.result_responses, dict):
                        team = self.sched.team_name
                        result = new.result_for_team(team)
                        if result:
                            result_res = self.result_responses.get(result, '')
                elif self.scores_are_different(old, new):
                    msg += "Score Updated:\r\n{}\r\n".format(new)
                if self.time_is_different(old, new) and new.future:
                    # Only notify if game hasn't already occurred
                    msg += ("Game Time Updated:\r\n"
                            "Game on {} is now: {}\r\n".format(
                                old['full_gametime_str'], new))
            if msg != '':
                self.send_msg(msg)
            if result_res != '':
                self.send_msg(result_res)

    def run(self):
        while not self.stopped:
            self.refresh_schedule()
            self.check_and_notify_schedule_changes()
            sleep(self.sleep_time)


class TestGamedayReminderBot(GamedayReminderBot):

    def send_msg(self, msg):
        print(msg)


class TestTeamFeeReminderBot(TeamFeeReminderBot):

    def send_msg(self, msg):
        print(msg)


class TestUpdatedGameNotifierBot(UpdatedGameNotifierBot):

    def send_msg(self, msg):
        print(msg)


def main():
    grb = GamedayReminderBot()
    grb.run()


if __name__ == '__main__':
    main()
