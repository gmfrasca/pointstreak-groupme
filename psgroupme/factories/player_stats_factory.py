from recleagueparser.player_stats.sportsengine_player_stats \
    import SportsEnginePlayerStats


class PlayerStatsFactory(object):

    def create(stats_type, **kwargs):
        if stats_type == 'sportsengine':
            return SportsEnginePlayerStats(**kwargs)
        else:
            raise ValueError("Stats Tool Type '{0}' not found"
                             .format(stats_type))

    create = staticmethod(create)
