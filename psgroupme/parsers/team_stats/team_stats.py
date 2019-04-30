from bs4 import BeautifulSoup
from requests import get
import datetime
import logging

LEAGUE_ID = 4601343
SEASON_ID = 565633


class TeamStats(object):

    STALE_TIME = 60

    def __init__(self, league_id=LEAGUE_ID, season_id=SEASON_ID, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.html_doc = None
        self.teams = list()
        self.last_refresh = datetime.datetime.now()
        self.url = self.get_stats_url(league_id, season_id)
        self.league_id = league_id
        self.season_id = season_id
        self.refresh_stats()

    def __repr__(self):
        """Prints the list of games in order to form a schedule"""
        return self.short_table

    @property
    def standings(self):
        return self.teams

    @property
    def short_table(self):
        return self._get_string_representation(short=True)

    @property
    def full_table(self):
        return self._get_string_representation(short=False)

    @property
    def is_stale(self):
        if self.html_doc is None:
            return True
        now = datetime.datetime.now()
        return (now - self.last_refresh).total_seconds() > self.STALE_TIME

    def _get_string_representation(self, short=False):
        res = ''
        for team in self.standings:
            rep = str(team) if short else team.full_description
            res += '{0}\r\n'.format(rep)
        return res

    def get_stats_url(self, league_id, season_id):
        raise NotImplementedError

    def get_team(self, search_name):
        self._logger.info("Searching for team: {}".format(search_name))
        if search_name.lower() == 'all':
            return self.standings
        found = list()
        for team in self.standings:
            if search_name.lower() in team.name.lower():
                found.append(team)
        self._logger.info("Found teams: {}".format(found))
        return found

    def get_team_stats(self):
        """Get a string representation of the current stats"""
        return str(self)

    def refresh_stats(self):
        """Reload the stats"""
        self._logger.info("Refreshing TeamStats")
        self.html_tables = self.retrieve_html_tables(self.url)
        self.teams = self.parse_table()

    def send_get_request(self, url):
        self._logger.info("Retreiving TeamStats from Website")
        self.html_doc = get(url).text
        self.last_refresh = datetime.datetime.now()

    def retrieve_html_tables(self, url):
        raise NotImplementedError

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
            self._logger.info("Team Stats are stale, must refresh")
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
