from psgroupme.bots.schedule_bot import ScheduleBot
from psgroupme.bots.playoff_bot import PlayoffBot
from psgroupme.bots.image_bot import ImageBot
from psgroupme.bots.player_stats_bot import PlayerStatsBot
from psgroupme.bots.team_stats_bot import TeamStatsBot
from psgroupme.bots.rsvp_bot import RsvpBot
import logging


class MasterBot(ImageBot, PlayoffBot, ScheduleBot, PlayerStatsBot,
                TeamStatsBot, RsvpBot):

    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        for baseclass in MasterBot.__bases__:
            self._logger.info("Initializing {} to MasterBot".format(baseclass))
            baseclass.__init__(self, *args, **kwargs)
