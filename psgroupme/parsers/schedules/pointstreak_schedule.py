"""
Quick and Dirty table parser to read a team schedule
off of Poinstreak, a team stats-tracking website
"""
from schedule import Schedule
from game import Game

# Default Poinstreak URL info
PS_URL = 'http://stats.pointstreak.com'
PS_SCHED_EXT = 'players/players-team-schedule.html'


class PointstreakSchedule(Schedule):
    """
    Represents a Team's Schedule, based on a given URL which points to
    a Poinstreak Team Schedule page
    """
    # Expected Column Data Contents
    COLUMNS = {
        'homelogo': 0,
        'hometeam': 1,
        'awaylogo': 2,
        'awayteam': 3,
        'gameday': 4,
        'gametime': 5,
        'extras': 6}

    def get_schedule_url(self, team_id, season_id):
        sched_params = 'teamid={0}&seasonid={1}'.format(team_id, season_id)
        return '{0}/{1}?{2}'.format(PS_URL, PS_SCHED_EXT, sched_params)

    def retrieve_html_table(self, url):
        return self.retrieve_html_table_with_class(url, 'nova-stats-table')

    def parse_table(self):
        """
        Get a list PoinstreakGames by parsing the raw html retrieved
        from the Poinstreak Team Schedule webpage

        Returns:
            a list of PoinstreakGames in order from first to last
        """
        games = []
        if self.html_table:
            for game_row in self.html_table.find_all('tr'):
                cells = game_row.find_all('td')
                gamedate = cells[self.COLUMNS['gameday']].string
                gametime = cells[self.COLUMNS['gametime']].string
                home, hscore = self.parse_team(cells[self.COLUMNS['hometeam']])
                away, ascore = self.parse_team(cells[self.COLUMNS['awayteam']])
                games.append(Game(gamedate,
                                  gametime,
                                  home,
                                  hscore,
                                  away,
                                  ascore))
        return games

    def parse_team(self, team_cell):
        """
        Parse a team name from the pointstreak schedule cell contents

        Args:
            team_cell (str): A Raw HTML string containing a link <a>
                to the team with the text containing the teamname, and
                (optionally) a <b> element containing a score

        Returns:
            A two-element tuple containing the plaintext team name and score
                (or None if it doesn't exist
        """
        name = team_cell.a.string
        score = team_cell.b.string.strip() if team_cell.b else None
        return name, score
