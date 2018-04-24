from factories import ScheduleFactory, RsvpToolFactory
from base_bot import BaseBot
import datetime


class ScheduleBot(BaseBot):

    NEXTGAME_RESPONSE = 'The next game is: {0}'
    LASTGAME_RESPONSE = 'The last game was: {0}'
    SCHEDULE_RESPONSE = 'This is the current schedule:\n{0}'
    DEFAULT_TEAM_ID = 3367048
    DEFAULT_SEASON_ID = 481539

    def __init__(self, bot_id, cfg_path=None, schedule=None, rsvp=None):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__(bot_id, cfg_path=cfg_path)
        self.schedule_type = self.bot_data.get('schedule_type', 'sportsengine')

        # Setup Pointstreak or SportsEngine Schedule
        team_id = self.bot_data.get('team_id', self.DEFAULT_TEAM_ID)
        season_id = self.bot_data.get('schedule_id', self.DEFAULT_SEASON_ID)
        sched_kwargs = dict(team_id=team_id, season_id=season_id)
        self.schedule = ScheduleFactory.create(self.schedule_type,
                                               **sched_kwargs) \
            if schedule is None else schedule

        # Set up RsvpTool
        self.rsvp = rsvp
        if rsvp is None and 'rsvp_tool_type' in self.bot_data:
            self.rsvp_tool_type = self.bot_data.get('rsvp_tool_type', 'tlr')
            self.rsvp_username = self.bot_data.get('rsvp_username', None)
            self.rsvp_password = self.bot_data.get('rsvp_password', None)
            if self.rsvp_username is not None and self.rsvp_password is \
                    not None:
                rsvp_kwargs = dict(username=self.rsvp_username,
                                   password=self.rsvp_password)
                self.rsvp = RsvpToolFactory.create(self.rsvp_tool_type,
                                                   **rsvp_kwargs)

    def get_extra_context(self):
        extra_context = super(ScheduleBot, self).get_extra_context()
        self.schedule.refresh_schedule()
        next_game = self.schedule.get_next_game()
        last_game = self.schedule.get_last_game()
        schedule = self.schedule.get_schedule()
        today = datetime.datetime.now().strftime("%a %b %d %I:%M.%S%p")
        attendance = self.rsvp.get_next_game_attendance() if self.rsvp \
            else None
        attendees = self.rsvp.get_next_game_attendees() if self.rsvp else None

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

        extra_context.update(dict(nextgame_resp=nextgame_resp,
                                  lastgame_resp=lastgame_resp,
                                  schedule_resp=schedule_resp,
                                  attendance_resp=attendance_resp,
                                  today=today,
                                  next_game=next_game,
                                  last_game=last_game,
                                  schedule=schedule,
                                  attendance=attendance,
                                  attendees=attendees))
        return extra_context

    def read_msg(self, msg):
        super(ScheduleBot, self).read_msg(msg)
        if self.rsvp is not None:
            self.check_rsvp(msg.get('name', None), msg.get('text', ''))

    def check_rsvp(self, sender, msg):
        name = sender if len(msg.split()) < 2 else msg.split(' ', 1)[1]
        try:
            if msg.startswith('!in'):
                self.rsvp.try_checkin(name, 'in')
            elif msg.startswith('!out'):
                self.rsvp.try_checkin(name, 'out')
        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def get_bot_specific_responses(self):
        return self.brm.get_responses().get('schedulebot', list())

    def respond(self, msg):
        """Respond using the matched message reply"""
        self.responder.reply(msg)
