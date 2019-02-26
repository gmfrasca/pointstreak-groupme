"""
Quick and Dirty table parser to read the player stats
off of SportsEngine, a team stats-tracking website
"""
from team_stats import TeamStats
from team import Team


SE_URL = 'http://www.pahl.org'
SE_STATS_EXT = 'standings/show'


class SportsEngineTeamStats(TeamStats):

    # Expected Column Data Contents
    COLUMNS = {
        'team_name': 0,
        'spacer': 1,
        'points': 2,
        'games_played': 3,
        'wins': 4,
        'losses': 5,
        'ties': 6,
        'goals_for': 7,
        'goals_against': 8,
        'division': 9
    }

    def get_stats_url(self, league_id, season_id):
        params = '{0}?subseason={1}'.format(league_id, season_id)
        return '{0}/{1}/{2}'.format(SE_URL, SE_STATS_EXT, params)

    def retrieve_html_tables(self, url):
        return self.retrieve_html_tables_with_class(url, 'statTable')

    def get_stat(self, row, data_name):
        return row[self.COLUMNS[data_name]].text.strip()

    # TODO
    def parse_table(self):
        standings = list()
        team_table = self.html_tables[0]
        for team_row in team_table.find_all('tr'):
            cells = team_row.find_all('td')
            team_name = self.get_stat(cells, 'team_name')
            team = Team(name=team_name,
                        points=self.get_stat(cells, 'points'),
                        games_played=self.get_stat(cells, 'games_played'),
                        wins=self.get_stat(cells, 'wins'),
                        losses=self.get_stat(cells, 'losses'),
                        ties=self.get_stat(cells, 'ties'),
                        goals_for=self.get_stat(cells, 'goals_for'),
                        goals_against=self.get_stat(cells, 'goals_against'),
                        division=self.get_stat(cells, 'division'))
            standings.append(team)
        return standings
