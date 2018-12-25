from bs4 import BeautifulSoup
from requests import get
import datetime

TEAM_ID = 3367048
SEASON_ID = 481539
COMPANY_ID = 'dreamsports'

# Unused for now, may be useful later for run limits in Amazon Lambda
FREE_REQUESTS = 1000000
FREE_COMP_TIME = 400000  # GB secs
ALLOCATED_MEMORY = 512  # MB
ESTIMATED_RUNTIME = 10  # secs
MAX_RESPONSES = 1024 * FREE_COMP_TIME / (ESTIMATED_RUNTIME * ALLOCATED_MEMORY)
MAX_RESPONSES = FREE_REQUESTS if MAX_RESPONSES > FREE_REQUESTS else \
    MAX_RESPONSES


class PlayerStats(object):

    STALE_TIME = 60

    def __init__(self, team_id=TEAM_ID, season_id=SEASON_ID,
                 company=COMPANY_ID, **kwargs):
        self.html_doc = None
        self.team_id = team_id
        self.season_id = season_id
        self.games = list()
        self.url = self.get_stats_url(team_id, season_id)
        self.refresh_stats()
        self.last_refresh = datetime.datetime.now()

    def __repr__(self):
        """Prints the list of games in order to form a schedule"""
        res = ''
        for player in self.players.get('players').values():
            res += '{0}\r\n'.format(str(player))
        for goalie in self.players.get('goalies').values():
            res += '{0}\r\n'.format(str(goalie))
        return res

    @property
    def is_stale(self):
        if self.html_doc is None:
            return True
        now = datetime.datetime.now()
        return (now - self.last_refresh).total_seconds() > self.STALE_TIME

    @property
    def roster_list(self):
        roster = self.players.get('players').values()
        roster.extend(self.players.get('goalies').values())
        return roster

    def get_player(self, search_name):
        if search_name.lower() == 'all':
            return self.roster_list
        found = list()
        for player_name, player in self.players.get('players').iteritems():
            if search_name.lower() in player_name.lower():
                found.append(player)
        for player_name, player in self.players.get('goalies').iteritems():
            if search_name.lower() in player_name.lower():
                found.append(player)
        return found

    def get_playoff_danger(self, sched_length, games_remaining):
        el_pars = dict(sched_length=sched_length,
                       games_remaining=games_remaining)
        for player in self.roster_list:
            if player.in_danger_of_inelligibility(**el_pars) and \
                    not player.is_playoff_eligible(sched_length):
                yield player

    def get_player_stats(self):
        """Get a string representation of the current stats"""
        return str(self)

    def refresh_stats(self):
        """Reload the stats"""
        self.html_tables = self.retrieve_html_tables(self.url)
        self.players = self.parse_table()

    def send_get_request(self, url):
            self.html_doc = get(url).text
            self.last_refresh = datetime.datetime.now()

    def retrieve_html_tables_with_class(self, url, table_class):
        """
        Retrieve the raw html for the table on a Poinstreak Team
        stats webpage

        Args:
            url (str): The URL to parse a Poinstreak stats from

        Returns:
             a list of bs tbody elements containing the player stats
        """
        if self.is_stale:
            self.send_get_request(url)
        soup = BeautifulSoup(self.html_doc, 'html.parser')
        tables = soup.find_all("table", {'class': table_class})
        processed = list()
        for table in tables:
            if table.tbody:
                processed.append(table.tbody)
            else:
                processed.append(table)
        return processed
