from factories import RsvpToolFactory
from base_bot import BaseBot


class RsvpBot(BaseBot):

    def __init__(self, bot_cfg, rsvp=None, *args, **kwargs):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(RsvpBot, self).__init__(bot_cfg, *args, **kwargs)
        self.rsvp = rsvp

    def checkin_player(self, *args, **kwargs):
        msg = kwargs.get('msg', dict())
        params = kwargs.get('params', list())
        name = msg.get('name', None) if len(params) < 1 else ' '.join(params)
        try:
            status = kwargs.get('checkin_type', 'in')
            self._load_rsvp()
            self.rsvp.try_checkin(name, status)
        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def load_rsvp(self, *args, **kwargs):
        super(RsvpBot, self).get_extra_context()
        self._load_rsvp()
        if self.rsvp is not None:
            attendance = self.rsvp.get_next_game_attendance()
            attendance_resp = attendance
            attendees = self.rsvp.get_next_game_attendees()
            lines = self.rsvp.get_next_game_lines()
            teamfee_progress = self.rsvp.get_team_fee_progress()
            self.context.update(dict(attendance=attendance,
                                     attendance_resp=attendance_resp,
                                     attendees=attendees,
                                     lines=lines,
                                     teamfee_progress=teamfee_progress))

    def _load_rsvp(self):
        # Set up RsvpTool
        if self.rsvp is not None:
            return
        if 'rsvp' in self.bot_data:
            rsvp_cfg = self.bot_data.get('rsvp')
            if 'username' in rsvp_cfg and 'password' in rsvp_cfg:
                rsvp_type = rsvp_cfg.get('type')
                rsvp_cfg.update(dict(rsvp_tool_type=rsvp_type))
                self.rsvp = RsvpToolFactory.create(**rsvp_cfg)
