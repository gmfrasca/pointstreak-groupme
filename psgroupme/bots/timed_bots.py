from factories import ScheduleFactory, RsvpToolFactory, PlayerStatsFactory
from factories import FinanceToolFactory
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

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def send_msg(self, msg):
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


class GamedayReminderBot(TimedBot):

    MORNING_CUTOFF = datetime.time(10, 00)
    NIGHT_CUTOFF = datetime.time(22, 00)
    DEFAULT_STATS_TYPE = 'sportsengine'

    def __init__(self, **kwargs):
        super(GamedayReminderBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.stats_cfg = kwargs.get('stats', dict())
        schedule_cfg = kwargs.get('schedule', dict())
        self.schedule_cfg = schedule_cfg
        self.schedule_type = self.schedule_cfg.get('type', 'pointstreak')
        self.rsvp = None
        self.load_rsvp()

    def load_rsvp(self):
        # Set up RsvpTool
        if self.rsvp is not None:
            return
        if 'rsvp' in self.bot_data:
            rsvp_cfg = self.bot_data.get('rsvp')
            if 'username' in rsvp_cfg and 'password' in rsvp_cfg:
                rsvp_type = rsvp_cfg.get('type')
                rsvp_cfg.update(dict(rsvp_tool_type=rsvp_type))
                self.rsvp = RsvpToolFactory.create(**rsvp_cfg)

    def load_stats(self):
        self.stats_type = self.bot_data.get(
            'stats_type',
            self.bot_data.get('schedule_type', self.DEFAULT_STATS_TYPE)
        )
        # TODO: remove
        stats_kwargs = dict(team_id=self.schedule_cfg.get('team_id'),
                            season_id=self.schedule_cfg.get('season_id'))
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
                if not self.game_has_been_notified(game_id) and \
                        self.ok_time_to_send_msg():
                    self.send_game_notification(game_id)


class TestGamedayReminderBot(GamedayReminderBot):

    def send_msg(self, msg):
        print(msg)


class TestTeamFeeReminderBot(TeamFeeReminderBot):

    def send_msg(self, msg):
        print(msg)


def main():
    grb = GamedayReminderBot()
    grb.run()


if __name__ == '__main__':
    main()
