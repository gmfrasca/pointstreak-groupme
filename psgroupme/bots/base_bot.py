from flask import request
from flask_restful import Resource
from interfaces.responder import Responder
from bot_responses import BotResponseManager
import datetime
import logging
import json
import re


class BaseBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    @property
    def bot_type(self):
        return type(self).__name__

    def __init__(self, bot_cfg, *args, **kwargs):
        """Load the config for this bot based on Name"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self.brm = BotResponseManager()
        self.bot_data = bot_cfg
        self.bot_id = self.bot_data.get('bot_id')
        self.bot_name = self.bot_data.get('bot_name', 'UnknownBot')
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)
        self.context = dict()

    def refresh_responses(self):
        self._logger.info("Refreshing Responses")
        self.responses = self.brm.get_global_responses()
        self.responses.extend(self.get_bot_specific_responses())

    def get_bot_specific_responses(self):
        """Override this method to add bot-specific responses"""
        return []

    def handle_msg(self, msg):
        """Check if a message is actionable (not system or bot), and respond"""
        self._logger.debug("Handling msg: {}".format(msg))
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if not system and sender_type != 'bot':
            self.read_msg(msg)

    def get_matching_responses(self, msg):
        self._logger.info("Searching for matching responses")
        context = msg.copy()
        context.update(self.bot_data)
        matches = [x for x in self.responses if re.search(
                   x['input'].format(**context), msg['text'], re.I | re.U)]
        self._logger.debug("Matching Responses: {}".format(matches))
        return matches

    def get_extra_context(self):
        self._logger.info("Getting Extra Context")
        self.context.update(self.brm.get_extra_context())
        self.context.update(dict(today=datetime.datetime.now().strftime(
            "%a %b %d %I:%M.%S%p")))

    def read_msg(self, msg):
        """
        Read a message's contents, and act on it if it matches a regex in
        self.responses.  Also updates the incoming message with the bot cfg for
        extra context (useful in replies, such as {bot_name})
        """
        if msg['text'] == '!ping':
            self.respond('pong')
        self.refresh_responses()
        matches = self.get_matching_responses(msg)
        if len(matches) > 0:
            self._logger.info("Reactable Msg Recieved!")
            matches = self.get_matching_responses(msg)
            self.context = msg.copy()
            self.context.update(self.bot_data)
            self.get_extra_context()
            for match in matches:
                self._logger.info("Working with match: {}".format(match))
                params = self.get_params(match, msg)
                try:
                    for action in self._get_actions(match):
                        action_type = action
                        kwargs = {}
                        if isinstance(action, dict):
                            action_type = action.get('type', 'pass')
                            kwargs = action.get('kwargs')
                            kwargs = kwargs if isinstance(kwargs, dict) else {}

                        self.react(action_type, msg, *params, **kwargs)
                    if 'reply' in match:
                        self.respond(match['reply'].format(**self.context))
                except KeyError:
                    # message requires undefined context variable
                    self.respond('Sorry, that command is not available.')

    def get_params(self, match, msg):
        ''' Get words after matching command in msgtxt and return as list '''
        cut_amt = len(match.get('input', '').split())
        words = msg.get('text', '').split()
        if len(words) <= cut_amt:
            return list()
        return words[cut_amt:]

    def react(self, action_type, msg, *args, **kwargs):
        self._logger.debug(("Reacting with:\n"
                            "    Action Type: {}\n"
                            "    Msg        : {}\n"
                            "    Args       : {}\n"
                            "    Kwargs     : {}\n").format(action_type, msg,
                                                            args, kwargs))
        if callable(getattr(self, action_type, None)):
            try:
                getattr(self, action_type)(msg, *args, **kwargs)
            except Exception:
                self._logger.exception("Could not perform the following action"
                                       ": {}".format(action_type))

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        self._logger.debug("Responding with msg: {}".format(msg))
        try:
            self.responder.reply(msg)
        except Exception:
            self._logger.info("Could not respond with message: {}".format(msg))

    def _get_actions(self, match):
        self._logger.info("Getting actions")
        actions = list()
        single_action = match.get('action', list())
        multi_actions = match.get('actions', list())
        if isinstance(single_action, basestring):
            actions.extend([single_action])
        if isinstance(single_action, list):
            actions.extend(single_action)
        if isinstance(multi_actions, basestring):
            actions.extend([multi_actions])
        if isinstance(multi_actions, list):
            actions.extend(multi_actions)
        self._logger.info("Actions to perform: {}".format(actions))
        return actions

    def get(self):
        """React to a GET call"""
        self._logger.info("Received GET call")
        return {'bot_cfg': self.bot_data}

    def post(self):
        """React to a POST call"""
        self._logger.info("Received POST call")
        data_str = request.data
        try:
            msg = json.loads(data_str)
            self.handle_msg(msg)
            return {'post': msg}
        except ValueError:
            pass
        return None
