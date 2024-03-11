from recleagueparser.schedules.compare import ScheduleComparer
from recleagueparser.schedules import ScheduleFactory
from .base_timed_bot import BaseTimedBot
from .test_timed_bot import TestTimedBot
from time import sleep
import threading
import datetime
import croniter

class ScheduleSyncCheckBot(BaseTimedBot):

    DEFAULT_CRON = "0 12 * * *"

    def __init__(self, **kwargs):
        super(ScheduleSyncCheckBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.debug = self.bot_data.get('debug')
        self.cron = self.bot_data.get('cron', self.DEFAULT_CRON)
        self.notify_days = self.bot_data.get('notify_days', 0)
        if not isinstance(self.notify_days, list):
            self.notify_days = [self.notify_days]
        self.notify_days = [int(x) for x in self.notify_days]

        self.schedule_cfg = self.bot_data.get('schedule', dict())
        self.schedule_type = self.schedule_cfg.get('type', 'pointstreak')

        self.cschedule_cfg = self.bot_data.get('compare_schedule', dict())
        self.cschedule_type = self.cschedule_cfg.get('type', 'pointstreak')
        self.include_past_games = self.cschedule_cfg.get('include_past_games', False)

    def check_for_diff_and_notify(self):
        try:
            self.schedule = ScheduleFactory.create(self.schedule_type,
                                                   **self.schedule_cfg)
            self.schedule.refresh_schedule()

            self.cschedule = ScheduleFactory.create(self.cschedule_type,
                                                   **self.cschedule_cfg)
            self.cschedule.refresh_schedule()
            self._logger.info("Checking Schedules for diffs...")
            if self.schedule is not None and self.cschedule is not None:
                sc = ScheduleComparer(self.schedule, self.cschedule)
                diff = sc.sched_diff(not self.include_past_games)
                if diff:
                    self.send_msg(f"ALERT: Schedule Diff Detected:\n{diff}")

        except Exception:
            self._logger.exception("Could Not Check Schedule diffs")

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
            t = threading.Timer(delta, self.check_for_diff_and_notify)
            t.daemon = True
            t.start()
            while t.is_alive():
                sleep(1)

class TestScheduleSyncCheckBot(TestTimedBot, ScheduleSyncCheckBot):
    pass
