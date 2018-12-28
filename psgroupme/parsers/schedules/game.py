from util import parsetime as pt


class Game(object):
    """Represents a game parsed from a Pointstreak schedule"""

    def __init__(self, date, time, hometeam, homescore, awayteam, awayscore,
                 year=None, prevgame=None):
        """ Store this game's relevant data """
        self.year = pt.determine_year(year)
        self.parse_date(date, time, self.year, prevgame)
        self.hometeam = hometeam
        self.homescore = homescore
        self.awayteam = awayteam
        self.awayscore = awayscore

    def parse_date(self, date, time, year, prevgame=None):
        # TODO: Determine if we should actually set includes_day
        self.date = pt.normalize_date(date.strip(), includes_day=True)
        self.time = pt.normalize_time(time.strip())
        self.full_gametime = pt.assemble_full_datetime(date, time, year)
        self.full_gametime_str = self.full_gametime.strftime(
            pt.FULL_DESCRIPTOR)
        if prevgame is not None:
            if prevgame.full_gametime > self.full_gametime:
                next_year = str(int(self.year) + 1)
                self.parse_date(date, time, next_year, prevgame)

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
