"""
Quick and Dirty table parser to read a team schedule
off of DashPlatform, a team stats-tracking website
"""
from util.parsetime import DATE_DESCRIPTOR, TIME_DESCRIPTOR
from bs4 import BeautifulSoup
from schedule import Schedule
import parsedatetime as pdt
import datetime
from game import Game

# *Red Hat 2 Dash*
TEAM_ID = 14998
SEASON_ID = 0
COMPANY_ID = 'dreamsports'


class DashPlatformSchedule(Schedule):

    DASH_URL = 'https://apps.dashplatform.com/'
    SCHEDULE_URL = '/dash/index.php?Action=Team/index'

    DEFAULT_COLUMNS = {
        'homescore': 2,
        'hometeam': 3,
        'awayscore': 4,
        'awayteam': 5,
    }

    def __init__(self, team_id=TEAM_ID, company_id=COMPANY_ID,
                 columns=None, **kwargs):
        super(DashPlatformSchedule, self).__init__(team_id=team_id,
                                                   company_id=company_id,
                                                   columns=columns, **kwargs)
        self.html_doc = None
        self.team_id = team_id
        self.company_id = company_id
        self.url = self.get_schedule_url(self.team_id, self.company_id)
        self.refresh_schedule()

    def get_schedule_url(self, team_id, company):
        sched_params = 'teamid={0}&company={1}'.format(team_id, company)
        return "{0}{1}&{2}".format(self.DASH_URL, self.SCHEDULE_URL,
                                   sched_params)

    def retrieve_html_table(self, url):
        table_class = 'list-group'
        if self.schedule_is_stale:
            self._logger.info("Schedule is stale, refreshing")
            self.send_get_request(url)
        soup = BeautifulSoup(self.html_doc, 'html.parser')
        return soup.find("div", {'class': table_class})

    def parse_table(self):
        """
        Get a list PoinstreakGames by parsing the raw html retrieved
        from the Poinstreak Team Schedule webpage

        Returns:
            a list of PoinstreakGames in order from first to last
        """
        self._logger.info("Parsing games from DashPlatform Data Table")
        games = []
        now = datetime.datetime.now()
        year = now.year
        if self.html_table:
            prevgame = None
            game_rows = self.html_table.find_all('div',
                                                 {'class': 'list-group-item'})
            for game_row in game_rows:
                # Parse Date
                gamedate_cell = game_row.find(
                    'div', {'class': 'event__date'}).div.find_all('div')
                cell_date = gamedate_cell[0].text
                cell_time = gamedate_cell[1].text.split(' ', 1)[1]
                structured = '{} {} {}'.format(cell_date, year, cell_time)
                parsed, _ = pdt.Calendar(
                    version=pdt.VERSION_CONTEXT_STYLE).parseDT(structured)
                gamedate = parsed.strftime(DATE_DESCRIPTOR)
                gametime = parsed.strftime(TIME_DESCRIPTOR)

                # Parse Score
                event_cells = game_row.find('div', {'class': 'event__details'})
                score_cells = event_cells.find_all('div', recursive=False)
                away_cells = score_cells[0].find_all('div')
                home_cells = score_cells[1].find_all('div')

                ascore = away_cells[1].text
                hscore = home_cells[1].text
                ascore = None if ascore == "-" else ascore
                hscore = None if hscore == "-" else hscore

                ateam = away_cells[0].a.text
                hteam = home_cells[0].a.text

                final = self.is_score_final(None)
                game = Game(gamedate, gametime, hteam, hscore,
                            ateam, ascore, prevgame=prevgame, final=final)
                games.append(game)
                prevgame = game
        self._logger.info("Parsed {} Games from Data Table".format(len(games)))
        return games

    def is_score_final(self, score):
        return False  # TODO: Implement

    def parse_game(self, game_cell):
        if game_cell.div:
            gamedate = game_cell.div
            gametime = gamedate.next_sibling
            return gamedate.text, gametime
        return 'Mon Jan 1st', '12:34pm'

    def parse_score(self, score_cell):
        if score_cell.b:
            score = score_cell.b.text.split()
            return score[0], score[2]
        return None, None

    def parse_teams(self, teams_cell):
        links = teams_cell.find_all('a')
        return links[0].text, links[1].text
