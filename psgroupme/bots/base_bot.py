from psgroupme.interfaces.responder import ResponderFactory
from psgroupme.bots.bot_responses import BotResponseManager
from psgroupme.util.encode_strings import encode_strings
import datetime
import logging
import json
import re


class BaseBot(object):
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
        self.bot_name = self.bot_data.get('bot_name', 'UnknownBot')
        self.bot_id = self.bot_data.get('bot_id')

        # Setup responders
        responders_cfg = self.bot_data.get('responders', [])
        if self.bot_id is not None:
            responders_cfg.append({"type": "groupme", "bot_id": self.bot_id})
        self.responders = self._setup_responders(responders_cfg, self.bot_id)

    def build_context(self, context=dict()):
        context.update(dict(
            bot_name=self.bot_name,
            today=datetime.datetime.now().strftime("%a %b %d %I:%M.%S%p"),
        ))
        return context

    def _setup_responders(self, responders_cfg, bot_id):
        responders = []
        for cfg in responders_cfg:
            responder_type = cfg.get('type', 'groupme')
            if 'bot_id' not in cfg:
                cfg['bot_id'] = bot_id

            self._logger.info(f"Setting up {responder_type} responder for bot {cfg['bot_id']}")
            responders.append(ResponderFactory().get_responder(responder_type, **cfg))
        return responders

    def refresh_responses(self):
        self._logger.info("Refreshing Responses")
        self.responses = self.brm.get_global_responses()
        self.responses.extend(self.get_bot_specific_responses())

    def get_bot_specific_responses(self):
        """Override this method to add bot-specific responses"""
        return []

    def _get_initial_context(self):
        initial_context = dict(
            today=datetime.datetime.now().strftime("%a %b %d %I:%M.%S%p"),
            bot_name=self.bot_name)
        initial_context.update(self.brm.get_extra_context())
        return initial_context

    def handle_msg(self, msg, metadata={}):
        """Check if a message is actionable (not system or bot), and respond"""
        self._logger.debug("Handling msg: {}".format(msg))
        initial_context = self._get_initial_context()
        initial_context.update(dict(text=msg))
        initial_context.update(metadata)
        self._logger.info("Initial Context: {}".format(initial_context))
        self.read_msg(initial_context)

    def get_matching_responses(self, context):
        self._logger.info("Searching for matching responses")
        msg = context['text']
        matches = [x for x in self.responses if re.search(
                   x['input'].format(**context), msg, re.I | re.U)]
        self._logger.debug("Matching Responses: {}".format(matches))
        return matches

    def read_msg(self, context):
        """
        Read a message's contents, and act on it if it matches a regex in
        self.responses.  Also updates the incoming message with the bot cfg for
        extra context (useful in replies, such as {bot_name})
        """
        msg = context['text']
        if msg == '!ping':
            self.respond('pong')
        self.refresh_responses()
        matches = self.get_matching_responses(context)
        if len(matches) > 0:
            self._logger.info("Reactable Msg Recieved!")
            matches = self.get_matching_responses(context)
            for match in matches:
                self._logger.info("Working with match: {}".format(match))
                params = self.get_params(match, msg)
                try:
                    # First, perform any requested actions
                    for action in self._get_actions(match):
                        action_type = action
                        kwargs = {}
                        if isinstance(action, dict):
                            action_type = action.get('type', 'pass')
                            kwargs = action.get('kwargs')
                            kwargs = kwargs if isinstance(kwargs, dict) else {}

                        self.react(action_type, msg, *params, **kwargs)

                    # Next, build the context after all actions have been performed
                    context = self.build_context(context)
                    self._logger.debug("Context: {}".format(context))

                    # Finally, respond to the message if reply is requested
                    if 'reply' in match:
                        rpls = match['reply']
                        rpls = rpls if isinstance(rpls, list) else [rpls]
                        self.respond([x.format(**context) for x in rpls])
                except KeyError:
                    # message requires undefined context variable
                    self.respond('Sorry, that command is not available.')

    def get_params(self, match, msg):
        ''' Get words after matching command in msgtxt and return as list '''
        cut_amt = len(match.get('input', '').split())
        words = msg.split()
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
                msg = encode_strings(msg)
                args = encode_strings(args)
                kwargs = encode_strings(kwargs)
                getattr(self, action_type)(msg, *args, **kwargs)
            except Exception:
                self._logger.exception("Could not perform the following action"
                                       ": {}".format(action_type))

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        for r in self.responders:
            try:
                self._logger.debug("Responding with msg: {}".format(msg))
                r.reply(msg)
            except Exception:
                self._logger.info("Could not respond with message using responder {}: {}".format(r.bot_id, msg))

    def _get_actions(self, match):
        self._logger.info("Getting actions")
        actions = list()
        single_action = match.get('action', list())
        multi_actions = match.get('actions', list())
        if isinstance(single_action, str):
            actions.extend([single_action])
        if isinstance(single_action, list):
            actions.extend(single_action)
        if isinstance(multi_actions, str):
            actions.extend([multi_actions])
        if isinstance(multi_actions, list):
            actions.extend(multi_actions)
        self._logger.info("Actions to perform: {}".format(actions))
        return actions