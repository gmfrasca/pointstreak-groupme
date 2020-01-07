from recleagueparser.team_stats.sportsengine_team_stats import (
    SportsEngineTeamStats)
from recleagueparser.team_stats.dashplatform_team_stats import (
    DashPlatformTeamStats)


class TeamStatsFactory(object):

    def create(stats_type, **kwargs):
        if stats_type == 'sportsengine':
            return SportsEngineTeamStats(**kwargs)
        elif stats_type == 'dash':
            return DashPlatformTeamStats(**kwargs)
        else:
            raise ValueError("Stats Tool Type '{0}' not found"
                             .format(stats_type))

    create = staticmethod(create)
