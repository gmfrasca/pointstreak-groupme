import parsedatetime as pdt
import datetime


# TIME_DESCRIPTOR = "%a %b %d %H:%M"  # 24-hour
TIME_DESCRIPTOR = "%a %b %d %I:%M%p"  # 12-hour


class Game(object):
    """Represents a game parsed from a Pointstreak schedule"""

    def __init__(self, date, time, hometeam, homescore, awayteam, awayscore,
                 year=None):
        """ Store this game's relevant data """
        self.date = date.strip()
        self.time = time.strip()
        self.full_gametime = self.assemble_full_gametime(date, time, year)
        self.full_gametime_str = self.full_gametime.strftime(TIME_DESCRIPTOR)
        self.hometeam = hometeam
        self.homescore = homescore
        self.awayteam = awayteam
        self.awayscore = awayscore

    def assemble_full_gametime(self, date, time, year=None):
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
        year = str(year if year else now.year)
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
