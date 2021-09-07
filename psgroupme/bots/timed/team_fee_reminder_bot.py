from recleagueparser.rsvp_tools import RsvpToolFactory as FinanceToolFactory
from .base_timed_bot import BaseTimedBot
from .test_timed_bot import TestTimedBot
from psgroupme.util import parsetime as pt
from time import sleep
import threading
import datetime
import croniter


class TeamFeeReminderBot(BaseTimedBot):

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
        # Set up FinanceTool
        self._logger.debug("Loading FinanceTool Parser")
        finance_cfg = self.finance_cfg.copy()
        if finance_cfg:
            if 'username' in finance_cfg and 'password' in finance_cfg:
                finance_type = finance_cfg.get('type')
                finance_cfg.update(dict(rsvp_tool_type=finance_type))
                return FinanceToolFactory.create(**finance_cfg)
        return None

    def post_msg(self):
        finance_tool = self.get_finance_tool()
        fee, paid, percent = finance_tool.get_team_fee_stats()
        # Run only if fee isn't fully paid
        if fee != paid:
            self._logger.info("Fee not paid in full yet, notifying")
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
        self._logger.info("Starting {} Thread".format(self.__class__.__name__))
        while not self.stopped:
            now = datetime.datetime.utcnow()
            cron = croniter.croniter(self.schedule, now)
            next_run = cron.get_next(datetime.datetime)
            delta = next_run - now
            self._logger.info("Next Run at: {}".format(next_run))
            t = threading.Timer(delta.total_seconds(), self.post_msg)
            t.daemon = True
            t.start()
            while t.is_alive():
                sleep(1)


class TestTeamFeeReminderBot(TestTimedBot, TeamFeeReminderBot):
    pass
