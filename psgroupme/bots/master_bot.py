from schedule_bot import ScheduleBot
from playoff_bot import PlayoffBot
from image_bot import ImageBot
from player_stats_bot import PlayerStatsBot
from team_stats_bot import TeamStatsBot
from rsvp_bot import RsvpBot


class MasterBot(ImageBot, PlayoffBot, ScheduleBot, PlayerStatsBot,
                TeamStatsBot, RsvpBot):

    def __init__(self, *args, **kwargs):
        for baseclass in MasterBot.__bases__:
            baseclass.__init__(self, *args, **kwargs)
