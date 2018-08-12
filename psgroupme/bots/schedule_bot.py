from factories import ScheduleFactory, RsvpToolFactory, PlayerStatsFactory
from base_bot import BaseBot
import datetime


class ScheduleBot(BaseBot):

    NEXTGAME_RESPONSE = 'The next game is: {0}'
    LASTGAME_RESPONSE = 'The last game was: {0}'
    SCHEDULE_RESPONSE = 'This is the current schedule:\n{0}'
    DEFAULT_TEAM_ID = 3367048
    DEFAULT_SEASON_ID = 481539
    DEFAULT_TYPE = 'sportsengine'

    def __init__(self, bot_cfg, schedule=None, rsvp=None, player_stats=None):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__(bot_cfg)
        self.schedule = schedule
        self.rsvp = rsvp
        self.player_stats = player_stats

    def load_schedule(self):
        if self.schedule is not None:
            return
        self.schedule_type = self.bot_data.get('schedule_type',
                                               self.DEFAULT_TYPE)

        # Setup Pointstreak or SportsEngine Schedule
        team_id = self.bot_data.get('team_id', self.DEFAULT_TEAM_ID)
        season_id = self.bot_data.get('schedule_id', self.DEFAULT_SEASON_ID)
        sched_kwargs = dict(team_id=team_id, season_id=season_id)
        self.schedule = ScheduleFactory.create(self.schedule_type,
                                               **sched_kwargs)

    def load_rsvp(self):
        # Set up RsvpTool
        if self.rsvp is not None:
            return
        if 'rsvp_tool_type' in self.bot_data:
            self.rsvp_tool_type = self.bot_data.get('rsvp_tool_type', 'tlr')
            self.rsvp_username = self.bot_data.get('rsvp_username', None)
            self.rsvp_password = self.bot_data.get('rsvp_password', None)
            if self.rsvp_username is not None and self.rsvp_password is \
                    not None:
                rsvp_kwargs = dict(username=self.rsvp_username,
                                   password=self.rsvp_password)
                self.rsvp = RsvpToolFactory.create(self.rsvp_tool_type,
                                                   **rsvp_kwargs)

    def load_player_stats(self):
        if self.player_stats is not None:
            return
        self.stats_type = self.bot_data.get(
            'stats_type',
            self.bot_data.get('schedule_type', self.DEFAULT_TYPE)
        )
        team_id = self.bot_data.get('team_id', self.DEFAULT_TEAM_ID)
        season_id = self.bot_data.get('schedule_id', self.DEFAULT_SEASON_ID)
        stats_kwargs = dict(team_id=team_id, season_id=season_id)
        self.player_stats = PlayerStatsFactory.create(self.stats_type,
                                                      **stats_kwargs)

    def get_extra_context(self):
        extra_context = super(ScheduleBot, self).get_extra_context()
        extra_context.update(dict(today=datetime.datetime.now().strftime(
            "%a %b %d %I:%M.%S%p")))
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

            extra_context.update(dict(nextgame_resp=nextgame_resp,
                                      lastgame_resp=lastgame_resp,
                                      schedule_resp=schedule_resp,
                                      next_game=next_game,
                                      last_game=last_game,
                                      schedule=schedule))

        if self.rsvp is not None:
            attendance = self.rsvp.get_next_game_attendance()
            attendance_resp = attendance
            attendees = self.rsvp.get_next_game_attendees()
            lines = self.rsvp.get_next_game_lines()
            teamfee_progress = self.rsvp.get_team_fee_progress()
            extra_context.update(dict(attendance=attendance,
                                      attendance_resp=attendance_resp,
                                      attendees=attendees,
                                      lines=lines,
                                      teamfee_progress=teamfee_progress))

        if self.player_stats is not None:
            roster = str(self.player_stats)
            extra_context.update(dict(roster=roster))
        return extra_context

    def react(self, msg, context):
        self.check_rsvp(msg.get('name', None), msg.get('text', ''))
        self.check_stat(msg, context)

    def check_rsvp(self, sender, msg):
        name = sender if len(msg.split()) < 2 else msg.split(' ', 1)[1]
        try:
            if msg.startswith('!in'):
                self.load_rsvp()
                self.rsvp.try_checkin(name, 'in')
            elif msg.startswith('!out'):
                self.load_rsvp()
                self.rsvp.try_checkin(name, 'out')
        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def check_stat(self, msg, context):
        sender = msg.get('name', None)
        text = msg.get('text', '')
        params = text.split()
        try:
            if text.startswith('!stat') and len(params) > 1:
                name = sender if len(params) < 3 else params[1]
                stat = params[2]
                self.load_player_stats()
                players = self.player_stats.get_player(name)
                if len(players) < 1:
                    self.respond(
                        "ERROR::Cound not find player: {0}".format(name))
                    return
                for player in players:
                    val = player.get_stat(stat.lower())
                    if val is not None:
                        if isinstance(val, float):
                            self.respond("{0}: {1:.3f} {2}".format(player.name,
                                                                   val,
                                                                   stat))
                        else:
                            self.respond('{0}: {1} {2}'.format(player.name,
                                                               val,
                                                               stat))
                    else:
                        self.respond(
                            "ERROR::Could not find stat: {0}".format(stat))

            elif text.startswith('!playoff'):
                self.load_player_stats()
                self.load_schedule()
                name = sender if len(params) < 2 else params[1]
                players = self.player_stats.get_player(name)
                if len(players) < 1:
                    self.respond(
                        "ERROR::Cound not find player: {0}".format(name))
                    return
                for player in players:
                    sched_length = self.schedule.length
                    games_remaining = self.schedule.games_remaining
                    el_pars = dict(sched_length=sched_length,
                                   games_remaining=games_remaining)
                    elligible = player.is_playoff_eligible(sched_length)
                    possible = player.can_be_elligible(**el_pars)
                    in_danger = player.in_danger_of_inelligibility(**el_pars)
                    missable = player.get_missable_games(**el_pars)
                    if elligible:
                        if name.lower() != 'all':
                            self.respond(
                                "{0} is elligible for playoffs".format(
                                    player.name))
                    elif possible:
                        if in_danger:
                            self.respond(("{0} is in danger of missing " +
                                          "playoffs.  They can miss {1} more" +
                                          " games").format(player.name,
                                                           missable))
                        elif name.lower() != 'all':
                            self.respond(("{0} is not in danger of missing " +
                                          "playoffs").format(player.name))
                    elif name.lower() != 'all':
                        self.respond(("It is not possible for {0} to be" +
                                      " elligible for playoffs").format(
                                          player.name))

        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def get_bot_specific_responses(self):
        return self.brm.get_responses().get('schedulebot', list())

    def respond(self, msg):
        """Respond using the matched message reply"""
        self.responder.reply(msg)

    def get_matching_responses(self, msg):
        matches = super(ScheduleBot, self).get_matching_responses(msg)
        for match in matches:
            if match.get('load_rsvp', False):
                self.load_rsvp()
            if match.get('load_schedule', False):
                self.load_schedule()
            if match.get('load_stats', False):
                self.load_player_stats()
        return matches
