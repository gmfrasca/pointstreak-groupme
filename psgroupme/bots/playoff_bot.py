from stats_bot import StatsBot
from schedule_bot import ScheduleBot


class PlayoffBot(ScheduleBot, StatsBot):

    def __init__(self, bot_cfg, *args, **kwargs):
        ScheduleBot.__init__(self, bot_cfg, *args, **kwargs)
        StatsBot.__init__(self, bot_cfg, *args, **kwargs)

    def check_playoff(self, msg, params, *args, **kwargs):
        name = msg.get('name', None) if len(params) < 0 else ' '.join(params)
        try:
            if len(params) > 0:
                self._load_player_stats()
                self._load_schedule()
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