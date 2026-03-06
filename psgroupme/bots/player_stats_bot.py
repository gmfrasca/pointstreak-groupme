from recleagueparser.player_stats import PlayerStatsFactory
from psgroupme.bots.base_bot import BaseBot


class PlayerStatsBot(BaseBot):

    def __init__(self, bot_cfg, player_stats=None, *args, **kwargs):
        super(PlayerStatsBot, self).__init__(bot_cfg, *args, **kwargs)
        self.player_stats = player_stats
        self.stats_cfg = self.bot_data.get('stats',
                                           self.bot_data.get('schedule'))
        self.player_stats_data = {}

    def check_stat(self, msg, *params, **kwargs):
        name = msg.get('name', None)
        try:
            if len(params) > 0:
                stat = params[-1]
                if len(params) > 1:
                    name = ' '.join(params[:-1])
                self._load_player_stats()
                self._logger.info("Retrieving stats for {}".format(name))
                players = self.player_stats.get_player(name)
                if len(players) < 1:
                    self.respond(
                        "ERROR::Cound not find player: {0}".format(name))
                    return
                for player in players:
                    self._logger.info("Checking {} stats for {}".format(
                        stat, player))
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
            self._logger.exception(e)
            self.respond("ERROR::{0}".format(str(e)))

    def load_player_stats(self, *args, **kwargs):
        self._logger.info("Getting Roster Data from PlayerStatsBot")
        self._load_player_stats()
        self.player_stats_data = dict(roster=self.player_stats)

    def build_context(self, context=dict()):
        self._logger.info("Adding Player Stats Data from PlayerStatsBot to Context")
        context.update(self.player_stats_data)
        return context

    def _load_player_stats(self):
        self._logger.debug("Loading PlayerStats Parser")
        if self.player_stats is not None:
            self._logger.debug("PlayerStats Parser already loaded.")
            return self.player_stats
        if self.stats_cfg is not None:
            self._logger.debug("PlayerStats Parser not loaded, "
                               "creating new one")
            stats_type = self.stats_cfg.get('type', self.DEFAULT_TYPE)
            self.stats_cfg.update(dict(stats_type=stats_type))
            self.player_stats = PlayerStatsFactory.create(**self.stats_cfg)
            return self.player_stats
