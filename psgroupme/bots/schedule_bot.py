from factories import ScheduleFactory
from base_bot import BaseBot


class ScheduleBot(BaseBot):

    NEXTGAME_RESPONSE = 'The next game is: {0}'
    LASTGAME_RESPONSE = 'The last game was: {0}'
    SCHEDULE_RESPONSE = 'This is the current schedule:\n{0}'
    DEFAULT_TEAM_ID = 3367048
    DEFAULT_SEASON_ID = 481539
    DEFAULT_TYPE = 'sportsengine'

    def __init__(self, bot_cfg, schedule=None, *args, **kwargs):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__(bot_cfg, *args, **kwargs)
        self.schedule = schedule

    def get_bot_specific_responses(self):
        return self.brm.get_responses().get('schedulebot', list())

    def load_schedule(self, *args, **kwargs):
        super(ScheduleBot, self).get_extra_context()
        self._load_schedule()
        if self.schedule is not None:
            self.schedule.refresh_schedule()  # TODO: do not need?
            next_game = self.schedule.get_next_game()
            last_game = self.schedule.get_last_game()
            schedule = self.schedule.get_schedule()
            nextgame_resp = self.NEXTGAME_RESPONSE.format(str(next_game))
            lastgame_resp = self.LASTGAME_RESPONSE.format(str(last_game))
            schedule_resp = self.SCHEDULE_RESPONSE.format(str(schedule))

            if next_game is None:
                nextgame_resp = "There are no games left on the schedule :("
            if last_game is None:
                lastgame_resp = "The season hasn't started yet"
            if schedule is None or len(self.schedule.games) < 1:
                schedule_resp = "No schedule yet :("

            self.context.update(dict(nextgame_resp=nextgame_resp,
                                     lastgame_resp=lastgame_resp,
                                     schedule_resp=schedule_resp,
                                     next_game=next_game,
                                     last_game=last_game,
                                     schedule=schedule))

    def _load_schedule(self):
        if self.schedule is not None:
            return
        if 'schedule' in self.bot_data:
            schedule_cfg = self.bot_data.get('schedule', dict())
            schedule_type = schedule_cfg.get('type', self.DEFAULT_TYPE)
            schedule_cfg.update(dict(schedule_type=schedule_type))
            self.schedule = ScheduleFactory.create(**schedule_cfg)
