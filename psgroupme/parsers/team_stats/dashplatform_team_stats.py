"""
Quick and Dirty table parser to read the player stats
off of SportsEngine, a team stats-tracking website
"""
from .team_stats import TeamStats
from .team import Team


DASH_URL = 'https://apps.dashplatform.com'
DASH_STATS_EXT = '/dash/index.php?Action=Team/index'


class DashPlatformTeamStats(TeamStats):

    # Expected Column Data Contents
    COLUMNS = {
        'team_name': 0,
        'spacer': 4,
        'points': 5,
        'games_played': 10,
        'wins': 1,
        'losses': 3,
        'ties': 2,
        'goals_for': 6,
        'goals_against': 7
    }

    def __init__(self, team_id, company_id, **kwargs):
        super(DashPlatformTeamStats, self).__init__(
            league_id=team_id, season_id=company_id)

    def get_stats_url(self, league_id, season_id):
        params = 'teamid={0}&company={1}'.format(league_id, season_id)
        return '{0}{1}&{2}#standings'.format(DASH_URL, DASH_STATS_EXT, params)

    def get_dash_stats(self, team_id, company):
        return self.get_stats(league_id=team_id, season_id=company)

    def retrieve_html_tables(self, url):
        self._logger.info("URL: {}".format(url))
        return self.retrieve_html_tables_with_class(url, 'table-striped')

    def get_stat(self, row, data_name):
        return row[self.COLUMNS[data_name]].text.strip()

    # TODO
    def parse_table(self):
        self._logger.info("Parsing TeamStats Page")
        standings = list()
        team_table = self.html_tables[0]
        for team_row in team_table.find_all('tr'):
            cells = team_row.find_all('td')
            if len(cells) > 0:
                team_name = self.get_stat(cells, 'team_name')
                wins = self.get_stat(cells, 'wins')
                ties = self.get_stat(cells, 'ties')
                losses = self.get_stat(cells, 'losses')
                division = "{}-{}-{}".format(wins, losses, ties)
                team = Team(name=team_name,
                            points=self.get_stat(cells, 'points'),
                            games_played=self.get_stat(cells, 'games_played'),
                            wins=wins,
                            losses=losses,
                            ties=ties,
                            goals_for=self.get_stat(cells, 'goals_for'),
                            goals_against=self.get_stat(
                                cells, 'goals_against'),
                            division=division)
                standings.append(team)
        return standings
