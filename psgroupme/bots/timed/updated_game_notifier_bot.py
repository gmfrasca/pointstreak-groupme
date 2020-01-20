from recleagueparser.schedules import ScheduleFactory
from .base_timed_bot import BaseTimedBot
from .test_timed_bot import TestTimedBot
from time import sleep
import datetime

EXPECTED_GAME_DURATION = 60 * 60 * 2  # 2 hours
ACTIVE_GAME_POLL_TIME = 60 * 2  # 2 minutes


class UpdatedGameNotifierBot(BaseTimedBot):

    NOTIFICATION_TYPES = ['GAMES_ADDED', 'GAMES_REMOVED',
                          'FINAL_SCORE', 'SCORE_UPDATED',
                          'TIME_UPDATED']

    def __init__(self, **kwargs):
        super(UpdatedGameNotifierBot, self).__init__(**kwargs)
        self.bot_data = kwargs
        self.schedule_cfg = self.bot_data.get('schedule', dict())
        self.sleep_time = self.schedule_cfg.get('sleep_time', 600)
        self.active_poll_time = self.schedule_cfg.get('active_poll_time',
                                                      ACTIVE_GAME_POLL_TIME)
        self.schedule_type = self.schedule_cfg.get('type', 'pointstreak')
        self.result_responses = self.bot_data.get('result_responses', dict())
        self.notify_caps = self.bot_data.get('notify', ['all'])
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
                sleep(60)

    def _notification_is_enabled(self, notify_type):
        if 'all' in [x.lower() for x in self.notify_caps]:
            return True
        return notify_type.lower() in [x.lower() for x in self.notify_caps]

    def store_old_games(self):
        self.old_games = list()
        for game in self.sched.games:
            self.old_games.append(game.data)

    def refresh_schedule(self):
        self._logger.debug("Refreshing Schedule")
        try:
            self.store_old_games()
            self.sched.refresh_schedule()
        except Exception:
            self._logger.warning("Could not refresh schedule")

    def scores_are_different(self, old_dict, new_game):
        old_home = old_dict['homescore']
        old_away = old_dict['awayscore']
        new_home = new_game.homescore
        new_away = new_game.awayscore
        self._logger.debug("Check Home Scores: {} vs {}".format(old_home,
                                                                new_home))
        self._logger.debug("Check Away Scores: {} vs {}".format(old_away,
                                                                new_away))
        return (old_dict['homescore'] != new_game.homescore or
                old_dict['awayscore'] != new_game.awayscore)

    def game_finality_is_different(self, old_dict, new_game):
        old = old_dict['final']
        new = new_game.final
        self._logger.debug("Check Finality: {} vs {}".format(old, new))
        return old != new

    def time_is_different(self, old_dict, new_game):
        old = old_dict['full_gametime_str']
        new = new_game.full_gametime_str
        self._logger.debug("Check Time: {} vs {}".format(old, new))
        return old != new

    def check_and_notify_schedule_changes(self):
        # TODO: Determine *WHICH* games were added or deleted
        # TODO: Check that game ids all match instead of assuming based on len
        self._logger.debug("Checking for changes in schedule...")
        if len(self.old_games) < len(self.sched.games):
            self._logger.info("More Games Detected: {} vs old {}".format(
                len(self.sched.games), len(self.old_games)))
            if self._notification_is_enabled('GAMES_ADDED'):
                self.send_msg("Schedule Change Detected: New Games Added!")
        elif len(self.old_games) > len(self.sched.games):
            self._logger.info("Less Games Detected: {} vs old {}".format(
                len(self.sched.games), len(self.old_games)))
            if self._notification_is_enabled('GAMES_REMOVED'):
                self.send_msg("Schedule Change Detected: Games Removed!")
        else:
            msg = ''
            result_res = ''
            for x in range(0, len(self.old_games)):
                old = self.old_games[x]
                new = self.sched.games[x]
                if (self.game_finality_is_different(old, new) and
                        self._notification_is_enabled('FINAL_SCORE')):
                    self._logger.info("Game {} has completed, ".format(x) +
                                      "Adding to Message List")
                    msg += "Final Score:\r\n{}\r\n".format(new)
                    if isinstance(self.result_responses, dict):
                        team = self.sched.team_name
                        result = new.result_for_team(team)
                        if result:
                            result_res = self.result_responses.get(result, '')
                elif (self.scores_are_different(old, new) and
                      self._notification_is_enabled('SCORE_UPDATED')):
                    self._logger.info("Score Updated for Game {},".format(x) +
                                      " Adding to Message List")
                    msg += "Score Updated:\r\n{}\r\n".format(new)
                if (self.time_is_different(old, new) and new.future and
                        self._notification_is_enabled('TIME_UPDATED')):
                    # Only notify if game hasn't already occurred
                    self._logger.info("Time Updated for Game {}, ".format(x) +
                                      "Adding to Message List")
                    msg += ("Game Time Updated:\r\n"
                            "Game on {} is now: {}\r\n".format(
                                old['full_gametime_str'], new))
            if msg != '':
                self.send_msg(msg)
            if result_res != '':
                self.send_msg(result_res)

    def game_is_in_progress(self):
        now = datetime.datetime.now()
        for game in self.sched.games:
            start = game.full_gametime
            sleep_delta = datetime.timedelta(seconds=self.sleep_time)
            game_delta = datetime.timedelta(seconds=EXPECTED_GAME_DURATION)
            cycle_before = start - sleep_delta
            cycle_after = start + sleep_delta + game_delta
            if not game.final and cycle_before > now and cycle_after < now:
                return True
        return False

    def sleep_until_next_run(self):
        sleep(self.sleep_time if self.game_is_in_progress else
              self.active_poll_time)

    def run(self):
        self._logger.info("Starting UpdatedGameNotificationBot")
        while not self.stopped:
            self.refresh_schedule()
            self.check_and_notify_schedule_changes()
            self.sleep_until_next_run()


class TestUpdatedGameNotifierBot(TestTimedBot, UpdatedGameNotifierBot):
    pass
