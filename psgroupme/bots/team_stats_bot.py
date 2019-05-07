from psgroupme.factories import TeamStatsFactory
from psgroupme.bots.base_bot import BaseBot


class TeamStatsBot(BaseBot):

    def __init__(self, bot_cfg, team_stats=None, *args, **kwargs):
        super(TeamStatsBot, self).__init__(bot_cfg, *args, **kwargs)
        self.team_stats = team_stats

    def check_team_stat(self, msg, *args, **kwargs):
        name = msg.get('name', None)  # TODO: this is wrong
        try:
            if len(args) > 0:
                stat = args[-1]
                if len(args) > 1:
                    name = ' '.join(args[:-1])
                self._load_team_stats()
                self._logger.info("Retrieving stats for {}".format(name))
                teams = self.team_stats.get_team(name)
                if len(teams) < 1:
                    self.respond(
                        "ERROR::Cound not find team: {0}".format(name))
                    return
                for team in teams:
                    self._logger.info("Looking up {} stats for {}".format(
                        stat, team))
                    val = team.get_stat(stat.lower())
                    if val is not None:
                        if isinstance(val, float):
                            self.respond("{0}: {1:.3f} {2}".format(team.name,
                                                                   val,
                                                                   stat))
                        else:
                            self.respond('{0}: {1} {2}'.format(team.name,
                                                               val,
                                                               stat))
                    else:
                        self._logger.warning(
                            "Could not find stat {} for {}".format(stat, team))
                        self.respond(
                            "ERROR::Could not find stat: {0}".format(stat))
        except Exception as e:
            self._logger.exception(e)
            self.respond("ERROR::{0}".format(str(e)))

    def get_standings(self, *args, **kwargs):
        super(TeamStatsBot, self).get_extra_context()
        self._logger.info("Getting Team Standings")
        self._load_team_stats()
        self.context.update(dict(standings=self.team_stats.short_table))

    def _load_team_stats(self):
        self._logger.debug("Loading TeamStats Parser")
        if self.team_stats is not None:
            self._logger.debug("TeamStats Parser alrady Loaded")
            return
        stats_cfg = self.bot_data.get('stats', self.bot_data.get('schedule'))
        if stats_cfg is not None:
            self._logger.debug("TeamStats Parser not loaded, creating new one")
            stats_type = stats_cfg.get('type', self.DEFAULT_TYPE)
            stats_cfg.update(dict(stats_type=stats_type))
            self.team_stats = TeamStatsFactory.create(**stats_cfg)
