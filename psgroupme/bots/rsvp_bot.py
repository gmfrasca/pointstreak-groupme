from recleagueparser.rsvp_tools import RsvpToolFactory
from psgroupme.bots.base_bot import BaseBot


class RsvpBot(BaseBot):

    def __init__(self, bot_cfg, rsvp=None, *args, **kwargs):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(RsvpBot, self).__init__(bot_cfg, *args, **kwargs)
        self.rsvp = rsvp
        self.rsvp_data = {}

    def checkin_player(self, msg, *args, **kwargs):
        checkin_type = kwargs.get("checkin_type", "in")
        name = msg.get('name', None) if len(args) < 1 else ' '.join(args)
        try:
            self._logger.info(
                "Received request to checkin {} with status {}".format(
                    name, checkin_type))
            self._load_rsvp()
            self.rsvp.try_checkin(name, checkin_type)
        except Exception as e:
            self._logger.exception(e)
            self.respond("ERROR::{0}".format(str(e)))

    def get_duty(self, msg, *args, **kwargs):
        duty_type = msg.get("duty_type", "Drinks") if len(args) < 1 else ' '.join(args)
        try:
            self._logger.info(f"Looking up {duty_type} duty assignment for upcoming game.")
            self._load_rsvp()
            d = "drinks" if duty_type.lower() == "beer" else duty_type
            assignee = self.rsvp.get_duty_assignment(d)
            if assignee:
                self.respond(f"{assignee} is assigned {duty_type} duty for upcoming game.")    
            else:
                self.respond(f"Could not find {duty_type} duty assignment for upcoming game.")

        except Exception as e:
            self._logger.exception(e)
            self.respond("ERROR::{0}".format(str(e)))

    def get_duties_responses(self):
        try:
            drink_duty = self.rsvp.get_duty_assignment("Drinks")
            all_duties = self.rsvp.get_all_duty_assignments()
            return drink_duty, all_duties
        except:
            return "", ""

    def get_players_checkin_notes(self):
        data = self.rsvp.get_next_game_data()
        player_list = data.get('all', list())
        note_items = [p for p in player_list if p.get('note')]
        notes = list()
        for n in note_items:
            player = n.get('player')
            note = n.get('note', "")
            notes.append(f"{player}: {note}")
        return '\r\n'.join(notes)

    def get_goalie_alert(self):
        goalies = self.rsvp.get_checked_in_goalies()
        if len(goalies) < 1:
            return "ALERT: No goalies checked in"
        return "Goalies checked in: {0}".format(', '.join([p.get('player') for p in goalies]))

    def load_rsvp(self, *args, **kwargs):
        self._logger.info("Getting RSVP Data from RsvpBot")
        self._load_rsvp()
        if self.rsvp is not None:
            self._logger.info("Getting Extra Context from RSVPTool Parser")
            attendance = self.rsvp.get_next_game_attendance()
            attendance_resp = attendance
            attendees = self.rsvp.get_next_game_attendees()
            lines = self.rsvp.get_next_game_lines()
            teamfee_progress = self.rsvp.get_team_fee_progress()
            drink_duty, all_duties = self.get_duties_responses()
            players_checkin_notes = self.get_players_checkin_notes()
            goalie_alert = self.get_goalie_alert()
            self.rsvp_data = dict(attendance=attendance,
                                        attendance_resp=attendance_resp,
                                        attendees=attendees,
                                        lines=lines,
                                        teamfee_progress=teamfee_progress,
                                        drink_duty=drink_duty,
                                        all_duties=all_duties,
                                        players_checkin_notes=players_checkin_notes,
                                        goalie_alert=goalie_alert)

    def build_context(self, context=dict()):
        self._logger.debug("Adding RSVP Data from RsvpBot to Context")
        context.update(self.rsvp_data)
        return context
    
    def _load_rsvp(self):
        # Set up RsvpTool
        self._logger.debug("Loading RSVPTool Parser")
        if self.rsvp is not None:
            self._logger.debug("RSVPTool Parser already loaded.")
            return
        if 'rsvp' in self.bot_data:
            self._logger.debug("RSVPTool Parser not loaded, creating new one")
            rsvp_cfg = self.bot_data.get('rsvp')
            rsvp_type = rsvp_cfg.get('type')
            rsvp_cfg.update(dict(rsvp_tool_type=rsvp_type))
            self.rsvp = RsvpToolFactory.create(**rsvp_cfg)
