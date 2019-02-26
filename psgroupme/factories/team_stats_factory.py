from parsers.team_stats.sportsengine_team_stats import SportsEngineTeamStats


class TeamStatsFactory(object):

    def create(stats_type, **kwargs):
        if stats_type == 'sportsengine':
            return SportsEngineTeamStats(**kwargs)
        else:
            raise ValueError("Stats Tool Type '{0}' not found"
                             .format(stats_type))

    create = staticmethod(create)
