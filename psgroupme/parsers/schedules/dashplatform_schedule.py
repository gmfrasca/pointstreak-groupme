"""
Quick and Dirty table parser to read a team schedule
off of DashPlatform, a team stats-tracking website
"""
from game import DATE_DESCRIPTOR, TIME_DESCRIPTOR
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

    # TODO
    DEFAULT_COLUMNS = {
        'gamedatetime': 0,
        'gametype': 1,
        'description': 2,
        'results': 3
    }

    def __init__(self, team_id=TEAM_ID, company=COMPANY_ID,
                 columns=None, **kwargs):
        self.html_doc = None
        self.team_id = team_id
        self.company = company
        self.url = self.get_schedule_url(self.team_id, self.company)
        self.refresh_schedule()

    def get_schedule_url(self, team_id, company):
        sched_params = 'teamid={0}&company={1}'.format(team_id, company)
        return "{0}{1}&{2}".format(self.DASH_URL, self.SCHEDULE_URL,
                                   sched_params)

    def retrieve_html_table(self, url):
        # As of 2018-04-10, this is no longer a table but a list
        # Leaving in incase this is undone
        # table_classes = 'table table-condensed table-striped'
        # return self.retrieve_html_table_with_class(url, table_classes)
        table_class = 'list-group'
        if self.schedule_is_stale:
            self.send_get_request(url)
        soup = BeautifulSoup(self.html_doc, 'html.parser')
        return soup.find("ul", {'class': table_class})

    def parse_table(self):
        """
        Get a list PoinstreakGames by parsing the raw html retrieved
        from the Poinstreak Team Schedule webpage

        Returns:
            a list of PoinstreakGames in order from first to last
        """
        games = []
        # OLD sytle
        # if self.html_table:
        #     for game_row in self.html_table.find_all('tr'):
        #         cells = game_row.find_all('td')
        #         gamedate, gametime = self.parse_game(
        #             cells[self.COLUMNS['gamedatetime']])
        #         hscore, ascore = self.parse_score(
        #             cells[self.COLUMNS['results']])
        #         home, away = self.parse_teams(
        #             cells[self.COLUMNS['description']])
        #         games.append(Game(gamedate,
        #                           gametime,
        #                           home,
        #                           hscore,
        #                           away,
        #                           ascore))
        now = datetime.datetime.now()
        year = now.year
        if self.html_table:
            for game_row in self.html_table.find_all('li'):
                gamedate_cell = game_row.find(
                    'h4', {'class': 'list-group-item-heading'}).text
                gamedate_list = gamedate_cell.split()
                structured = '{}/{} {}'.format(gamedate_list[0], year,
                                               gamedate_list[2])
                parsed, _ = pdt.Calendar().parseDT(structured)
                gamedate = parsed.strftime(DATE_DESCRIPTOR)
                gametime = parsed.strftime(TIME_DESCRIPTOR)
                score_cells = game_row.find_all('td')
                hscore = score_cells[0].text
                hteam = score_cells[1].a.text
                ascore = score_cells[2].text
                ateam = score_cells[3].a.text
                games.append(Game(gamedate,
                                  gametime,
                                  hteam,
                                  hscore,
                                  ateam,
                                  ascore))
        return games

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
