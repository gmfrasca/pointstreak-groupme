from factories import ScheduleFactory, RsvpToolFactory
from base_bot import BaseBot
import datetime
import bot_responses


class ScheduleBot(BaseBot):

    SPECIFIC_SET_RESPONSES = bot_responses.SCHEDULE_BOT_RESPONSES
    NEXTGAME_RESPONSE = 'The next game is: {0}'
    LASTGAME_RESPONSE = 'The last game was: {0}'
    SCHEDULE_RESPONSE = 'This is the current schedule:\n{0}'
    DEFAULT_TEAM_ID = 3367048
    DEFAULT_SEASON_ID = 481539

    def __init__(self, bot_id, cfg_path=None, schedule=None, tlr=None):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__(bot_id, cfg_path=cfg_path)
        self.schedule_type = self.bot_data.get('schedule_type', 'sportsengine')
        self.rsvp_tool_type = self.bot_data.get('rsvp_tool_type', 'tlr')

        # Setup Pointstreak or SportsEngine Schedule
        team_id = self.bot_data.get('team_id', self.DEFAULT_TEAM_ID)
        season_id = self.bot_data.get('schedule_id', self.DEFAULT_SEASON_ID)
        sched_kwargs = dict(team_id=team_id, season_id=season_id)
        self.schedule = ScheduleFactory.create(self.schedule_type,
                                               **sched_kwargs) \
            if schedule is None else schedule

        # Set up TeamLockerRoom
        self.tlr = tlr
        if tlr is None:
            self.tlr_username = self.bot_data.get('tlr_username', None)
            self.tlr_password = self.bot_data.get('tlr_password', None)
            if self.tlr_username is not None and self.tlr_password is not None:
                tlr_kwargs = dict(username=self.tlr_username,
                                  password=self.tlr_password)
                self.tlr = RsvpToolFactory.create(self.rsvp_tool_type,
                                                  tlr_kwargs)

    def get_bot_specific_responses(self):
        self.schedule.refresh_schedule()
        next_game = self.schedule.get_next_game()
        last_game = self.schedule.get_last_game()
        schedule = self.schedule.get_schedule()
        today = datetime.datetime.now().strftime("%a %b %d %I:%M.%S%p")
        attendance = self.tlr.get_next_game_attendance() if self.tlr else None

        nextgame_resp = self.NEXTGAME_RESPONSE.format(str(next_game))
        lastgame_resp = self.LASTGAME_RESPONSE.format(str(last_game))
        schedule_resp = self.SCHEDULE_RESPONSE.format(str(schedule))
        attendance_resp = attendance

        if next_game is None:
            nextgame_resp = "There are no games left on the schedule :("
        if last_game is None:
            lastgame_resp = "The season hasn't started yet"
        if schedule is None or len(self.schedule.games) < 1:
            schedule_resp = "No schedule yet :("

        responses = [
            {
                'input': r'when.*next game([\?\!\.( is)].*)??$',
                'reply': nextgame_resp
            },
            {
                'input': r'what was the score\??',
                'reply': lastgame_resp
            },
            {
                'input': r'^how(\'d| did)? we do([\?\!\.].*)??$',
                'reply': lastgame_resp
            },
            {
                'input': r'what is.* schedule([\?\!\.].*)??$',
                'reply': schedule_resp
            },
            {
                'input': r'^how many do we have',
                'reply': attendance_resp
            },
            {
                'input': r'^what is today$',
                'reply': today
            }
        ]
        return responses

    def respond(self, msg):
        """Respond using the matched message reply"""
        self.responder.reply(msg)
