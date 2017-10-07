from flask import request
from flask_restful import Resource
from responder import Responder
from config_manager import ConfigManager
from team_schedule import PointstreakSchedule
import datetime
import bot_responses
import json
import re


class BaseBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    SPECIFIC_SET_RESPONSES = None

    @property
    def bot_type(self):
        return type(self).__name__

    def __init__(self, cfg_path=None):
        """Load the config for this bot based on Name"""
        # Get the Bot Config
        self.cfg_mgr = ConfigManager(cfg_path)
        self.bot_data = self.cfg_mgr.get_bot_data(self.bot_type)
        self.bot_id = self.cfg_mgr.get_bot_id(self.bot_type)
        self.bot_id = self.bot_data.get('bot_id')
        self.bot_name = self.bot_data.get('bot_name', 'UnknownBot')
        self.group_id = self.bot_data.get('group_id', 'UnknownGroup')
        self.group_name = self.bot_data.get('group_name', 'UnknownGroup')
        self.callback_url = self.bot_data.get('callback_url', None)
        self.avatar_url = self.bot_data.get('avatar_url', None)

        assert self.bot_id is not None

        # Set up the Responder
        self.responder = Responder(self.bot_id)
        self.refresh_responses()

    def refresh_responses(self):
        self.responses = list(bot_responses.GLOBAL_RESPONSES)
        self.responses.extend(self.get_bot_specific_responses())

        if self.SPECIFIC_SET_RESPONSES is not None:
            self.responses.extend(self.SPECIFIC_SET_RESPONSES)

    def get_bot_specific_responses(self):
        """Override this method to add bot-specific responses"""
        return []

    def handle_msg(self, msg):
        """Check if a message is actionable (not system or bot), and respond"""
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if not system and sender_type != 'bot':
            self.read_msg(msg)

    def read_msg(self, msg):
        """
        Read a message's contents, and act on it if it matches a regex in
        self.responses.  Also updates the incoming message with the bot cfg for
        extra context (usefull in replies, such as {bot_name})
        """
        self.refresh_responses()

        context = msg.copy()
        context.update(self.bot_data)
        matches = [x for x in self.responses if re.search(
           x['input'].format(**context), msg['text'], re.I | re.U)]
        if len(matches) > 0:
            self.respond(matches[0]['reply'].format(**context))

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        self.responder.reply('Hello, this is {0}'.format(self.bot_name))

    def get(self):
        """React to a GET call"""
        return {'bot_cfg': self.bot_data}

    def post(self):
        """React to a POST call"""
        data_str = request.data
        try:
            msg = json.loads(data_str)
            self.handle_msg(msg)
            return {'post': msg}
        except ValueError:
            pass
        return None


class ScheduleBot(BaseBot):

    SPECIFIC_SET_RESPONSES = bot_responses.SCHEDULE_BOT_RESPONSES
    NEXTGAME_RESPONSE = 'The next game is: {0}'
    LASTGAME_RESPONSE = 'The last game was: {0}'
    SCHEDULE_RESPONSE = 'This is the current schedule:\n{0}'

    def __init__(self, cfg_path=None, schedule=None):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        self.schedule = PointstreakSchedule() if schedule is None else schedule
        super(ScheduleBot, self).__init__(cfg_path=cfg_path)

    def get_bot_specific_responses(self):
        self.schedule.refresh_schedule()
        next_game = self.schedule.get_next_game()
        last_game = self.schedule.get_last_game()
        schedule = self.schedule.get_schedule()
        today = datetime.datetime.now().strftime("%a %b %d %I:%M.%S%p")

        nextgame_resp = self.NEXTGAME_RESPONSE.format(str(next_game))
        lastgame_resp = self.LASTGAME_RESPONSE.format(str(last_game))
        schedule_resp = self.SCHEDULE_RESPONSE.format(str(schedule))

        if next_game is None:
            nextgame_resp = "There are no games left on the schedule :("
        if last_game is None:
            lastgame_resp = "The season hasn't started yet"
        if schedule is None or len(self.schedule.games) < 1:
            schedule_resp = "No schedule yet :("

        responses = [
            {
                'input': r'when.*next game([\?\!\.( is)].*)??$',
                'reply': nextgame_resp
            },
            {
                'input': r'what was the score\??',
                'reply': lastgame_resp
            },
            {
                'input': r'^how(\'d| did)? we do([\?\!\.].*)??$',
                'reply': lastgame_resp
            },
            {
                'input': r'what is.* schedule([\?\!\.].*)??$',
                'reply': schedule_resp
            },
            {
                'input': r'^what is today$',
                'reply': today
             }
        ]
        return responses

    def respond(self, msg):
        """Respond using the matched message reply"""
        self.responder.reply(msg)


class HockeyBot(ScheduleBot):
    """Just a clone of ScheduleBot, with a different bot name"""

class TestBot(HockeyBot):
    """Debug"""
    def respond(self, msg):
        """Respond using the matched message reply"""
        print(msg)

