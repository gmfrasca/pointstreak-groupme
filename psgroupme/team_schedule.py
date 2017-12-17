"""
Quick and Dirty table parser to read a team schedule
off of Poinstreak, a team stats-tracking website
"""
import parsedatetime as pdt
from bs4 import BeautifulSoup
from requests import get
import datetime

# Unused for now, may be useful later for run limits in Amazon Lambda
FREE_REQUESTS = 1000000
FREE_COMP_TIME = 400000  # GB secs
ALLOCATED_MEMORY = 512  # MB
ESTIMATED_RUNTIME = 10  # secs
MAX_RESPONSES = 1024 * FREE_COMP_TIME / (ESTIMATED_RUNTIME * ALLOCATED_MEMORY)
MAX_RESPONSES = FREE_REQUESTS if MAX_RESPONSES > FREE_REQUESTS else \
    MAX_RESPONSES

# Default Poinstreak URL info
PS_URL = 'http://stats.pointstreak.com'
PS_SCHED_EXT = 'players/players-team-schedule.html'
SE_URL = 'http://www.pahl.org'
SE_SCHED_EXT = 'schedule/team_instance'

# **Team Info**
# *Sharknados*
#TEAM_ID = 666456
#SEASON_ID = 17455
# *DnC SportEngine*
#TEAM_ID = 2945251
#SEASON_ID = 422822
# *Sharknados SportsEngine*
TEAM_ID = 3367048
SEASON_ID = 481539

# TIME_DESCRIPTOR = "%a %b %d %H:%M"  # 24-hour
TIME_DESCRIPTOR = "%a %b %d %I:%M%p"  # 12-hour


class ScheduleFactory(object):

    def create(schedule_type, **kwargs):
        if schedule_type == 'pointstreak':
            return PointstreakSchedule(**kwargs)
        elif schedule_type == 'sportsengine':
            return SportsEngineSchedule(**kwargs)
        else:
            raise ValueError("Schedule Type '{0}' not found"
                             .format(schedule_type))

    create = staticmethod(create)


class Game(object):
    """Represents a game parsed from a Pointstreak schedule"""

    def __init__(self, date, time, hometeam, homescore, awayteam, awayscore):
        """ Store this game's relevant data """
        self.date = date.strip()
        self.time = time.strip()
        self.full_gametime = self.assemble_full_gametime(date, time)
        self.full_gametime_str = self.full_gametime.strftime(TIME_DESCRIPTOR)
        self.hometeam = hometeam
        self.homescore = homescore
        self.awayteam = awayteam
        self.awayscore = awayscore

    def assemble_full_gametime(self, date, time):
        """
        Get a parsable full gametime (date + time) based on a
        human-readable date (ex: Wed, Aug 5) and Time

        Args:
            date (str): A human-readable date string, like 'Wed, Aug 5'
            time (str): A human-readable time string, like '8:45 PM'

        Returns:
            a parsed pdt object representing the input date and time
        """
        now = datetime.datetime.now()
        # TODO: right now we assume games are in the same year because
        # Pointstreak does not give us a better way to determine it
        year = str(now.year)
        full_gametime = date.split()[1:]
        if full_gametime[0] in ['Jan', 'Feb', 'Mar'] and now.month > 7:
            year = str(now.year + 1)
        full_gametime.extend([year])
        full_gametime.extend(time.split())
        full_gametime = ' '.join(full_gametime)

        # TODO: act on bad status from parseDT
        parsed, status = pdt.Calendar().parseDT(str(full_gametime))
        return parsed

    def __repr__(self):
        """Print this game's most relevant info all together"""
        if self.homescore and self.awayscore:
            return '{0} {1} : {2} {3} on {4}'.format(self.hometeam,
                                                     self.homescore,
                                                     self.awayteam,
                                                     self.awayscore,
                                                     self.full_gametime_str)
        return '{0} vs {1} at {2}'.format(self.hometeam,
                                          self.awayteam,
                                          self.full_gametime_str)


class Schedule(object):

    def __init__(self, team_id=TEAM_ID, season_id=SEASON_ID):
        self.team_id = TEAM_ID
        self.season_id = SEASON_ID
        self.url = self.get_schedule_url(team_id, season_id)
        self.refresh_schedule()

    def __repr__(self):
        """Prints the list of games in order to form a schedule"""
        res = ''
        for game in self.games:
            res += '{0}\n'.format(game)
        return res

    def get_schedule(self):
        """Get a string representation of the current schedule"""
        self.refresh_schedule()
        return str(self)

    def get_next_game_after(self, target_datetime):
        """
        Get the next game after a given time

        Args:
            target_datetime (str): The given time to check for games after

        Returns:
            the next game after :target_datetime:
        """
        self.refresh_schedule()
        for game in self.games:
            if game.full_gametime > target_datetime:
                return game
        return None

    def get_last_game_before(self, target_datetime):
        """
        Get the last game before a given time

        Args:
            target_datetime (str): The given time to check for games before

        Returns:
            the last game before :target_datetime:
        """
        self.refresh_schedule()
        last_game = None
        for game in self.games:
            last_game = game if game.full_gametime < target_datetime \
                else last_game
        return last_game

    def get_next_game(self):
        """
        Get the next game after right now

        Returns:
            the next game after right now
        """
        return self.get_next_game_after(datetime.datetime.now())

    def get_last_game(self):
        """
        Get the last game before right now

        Returns:
            the last game before right now
        """
        return self.get_last_game_before(datetime.datetime.now())

    def refresh_schedule(self):
        """Reload the schedule from pointstreak"""
        self.html_table = self.retrieve_html_table(self.url)
        self.games = self.parse_table()

    def retrieve_html_table_with_class(self, url, table_class):
        """
        Retrieve the raw html for the table on a Poinstreak Team
        Schedule webpage

        Args:
            url (str): The URL to parse a Poinstreak Schedule from

        Returns:
             a bs tbody element containing the team schedule
        """
        html_doc = get(url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        table = soup.find("table", {'class': table_class})
        return table.tbody


class SportsEngineSchedule(Schedule):

    # Expected Column Data Contents
    COLUMNS = {
        'homelogo': None,
        'hometeam': None,
        'awaylogo': None,
        'awayteam': 2,
        'gameday': 0,
        'gametime': 4,
        'extras': None,
        'result': 1,
        'location': 2
    }

    def __init__(self, **kwargs):
        self.team_name = 'blah'
        super(SportsEngineSchedule, self).__init__(**kwargs)
        self.team_name = self.parse_team_name()

    def parse_team_name(self):
        html_doc = get(self.url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup.h2.a.text

    def get_schedule_url(self, team_id, season_id):
        # TODO subseason may not be necessary, appears to default with latest
        sched_params = '{0}?subseason={1}'.format(team_id, season_id)
        return '{0}/{1}/{2}'.format(SE_URL, SE_SCHED_EXT, sched_params)

    def retrieve_html_table(self, url):
        return self.retrieve_html_table_with_class(
            url, 'statTable sortable noSortImages')

    def parse_table(self):
        games = []
        for game_row in self.html_table.find_all('tr'):
            cells = game_row.find_all('td')
            gamedate = cells[self.COLUMNS['gameday']].text
            gametime = self.get_game_time(cells[self.COLUMNS['gametime']])
            hometeam, awayteam = self.parse_teams(
                cells[self.COLUMNS['awayteam']])
            homescore, awayscore = self.parse_score(
                cells[self.COLUMNS['result']],
                cells[self.COLUMNS['awayteam']])
            game = Game(gamedate, gametime, hometeam, homescore, awayteam,
                        awayscore)
            games.append(game)
        return games

    def is_home_team(self, opponent):
        return True if opponent.div.text.strip()[:1] == '@' else False

    def get_game_time(self, gametime_cell):
        gametime = gametime_cell.a if gametime_cell.a is not None else None
        if gametime is not None and gametime.span is not None:
            return gametime.text
        return "12:01 AM EST"

    def parse_teams(self, opponent):
        if self.is_home_team(opponent):
            return self.team_name, opponent.div.a.text
        return opponent.div.a.text, self.team_name

    def parse_score(self, score, opponent):
        if score.div is None or score.div.a is None:
            return None, None
        scoretext = score.div.a.text
        scores = scoretext.split('-')
        if self.is_home_team(opponent):
            return scores[0], scores[1]
        return scores[1], scores[0]


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


def main(schedule_type='sportsengine'):
    """
    This is more of a testing procedure.  Get all relevent info and print it
    """
    schedule = ScheduleFactory.create(schedule_type)
    now = datetime.datetime.now()
    next_game = schedule.get_next_game()
    last_game = schedule.get_last_game()
    print "--- Today's Date ---"
    print now
    print "--- Full Schedule ---"
    print schedule.get_schedule()
    print "--- Next Game on Schedule ---"
    if not next_game:
        print 'No games left on schedule'
    else:
        print 'The next game is {0}'.format(next_game)
    print "--- Last Game Played ---"
    if not last_game:
        print 'No games have been played yet'
    else:
        print 'The last game was {0}'.format(last_game)


if __name__ == "__main__":
    main()
