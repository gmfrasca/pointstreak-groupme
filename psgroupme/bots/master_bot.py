from schedule_bot import ScheduleBot
from image_bot import ImageBot


class MasterBot(ScheduleBot, ImageBot):

    def __init__(self, *args, **kwargs):
        for baseclass in MasterBot.__bases__:
            baseclass.__init__(self, *args, **kwargs)
