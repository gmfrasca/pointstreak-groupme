from schedule_bot import ScheduleBot
from playoff_bot import PlayoffBot
from image_bot import ImageBot
from stats_bot import StatsBot
from rsvp_bot import RsvpBot


class MasterBot(ImageBot, PlayoffBot, ScheduleBot, StatsBot, RsvpBot):

    def __init__(self, *args, **kwargs):
        for baseclass in MasterBot.__bases__:
            baseclass.__init__(self, *args, **kwargs)
