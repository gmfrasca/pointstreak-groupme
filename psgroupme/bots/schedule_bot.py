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

    def __init__(self, bot_cfg, schedule=None, rsvp=None, player_stats=None,
                 *args, **kwargs):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__(bot_cfg)
        self.schedule = schedule
        self.rsvp = rsvp
        self.player_stats = player_stats

    def load_schedule(self):
        if self.schedule is not None:
            return
        if 'schedule' in self.bot_data:
            schedule_cfg = self.bot_data.get('schedule', dict())
            schedule_type = schedule_cfg.get('type', self.DEFAULT_TYPE)
            schedule_cfg.update(dict(schedule_type=schedule_type))
            self.schedule = ScheduleFactory.create(**schedule_cfg)

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

    def load_player_stats(self):
        if self.player_stats is not None:
            return
        stats_cfg = self.bot_data.get('stats', self.bot_data.get('schedule'))
        if stats_cfg is not None:
            stats_type = stats_cfg.get('type', self.DEFAULT_TYPE)
            stats_cfg.update(dict(stats_type=stats_type))
            self.player_stats = PlayerStatsFactory.create(**stats_cfg)

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

    def react(self, action_type, msg, context, params):
        super(ScheduleBot, self).react(action_type, msg, context, params)
        # self.check_stat(msg, context)

    def checkin_player(self, *args, **kwargs):
        msg = kwargs.get('msg', dict())
        params = kwargs.get('params', list())
        name = msg.get('name', None) if len(params) < 1 else ' '.join(params)
        try:
            self.load_rsvp()
            self.rsvp.try_checkin(name, kwargs.get('checkin_type', 'in'))
        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def check_stat(self, msg, params, **kwargs):
        name = msg.get('name', None)
        try:
            if len(params) > 0:
                stat = params[-1]
                if len(params) > 1:
                    name = ' '.join(params[:-1])
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
        except Exception as e:
            self.respond("ERROR::{0}".format(str(e)))

    def check_playoff(self, msg, params, *args, **kwargs):
        name = msg.get('name', None) if len(params) < 0 else ' '.join(params)
        try:
            if len(params) > 0:
                self.load_player_stats()
                self.load_schedule()
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
