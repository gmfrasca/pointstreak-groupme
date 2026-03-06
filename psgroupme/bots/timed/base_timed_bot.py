import threading
import logging
from psgroupme.interfaces.responder import ResponderFactory


class BaseTimedBot(threading.Thread):

    def __init__(self, **kwargs):
        """Load the config for this bot based on Name"""
        super(BaseTimedBot, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stop_event = threading.Event()
        self.daemon = True
        self.bot_id = kwargs.get('bot_id')

        # Setup responders
        responders_cfg = kwargs.get('responders', [])
        if self.bot_id is not None:
            responders_cfg.append({"type": "groupme", "bot_id": self.bot_id})
        self.responders = self._setup_responders(responders_cfg, self.bot_id)

    def _setup_responders(self, responders_cfg, bot_id):
        responders = []
        for cfg in responders_cfg:
            responder_type = cfg.get('type', 'groupme')
            if 'bot_id' not in cfg:
                cfg['bot_id'] = bot_id

            self._logger.info(f"Setting up {responder_type} responder for bot {cfg['bot_id']}")
            responders.append(ResponderFactory().get_responder(responder_type, **cfg))
        return responders

    @property
    def bot_type(self):
        return type(self).__name__

    def run(self):
        # Override This
        return True

    def stop(self):
        self._logger.info("Stopping Bot {0}".format(self.bot_type))
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def send_msg(self, msg):
        if msg and msg != '':
            for r in self.responders:
                try:
                    self._logger.debug("Sending msg: {}".format(msg))
                    r.reply(msg)
                except Exception:
                    self._logger.info("Could not send message using responder {}: {}".format(r.bot_id, msg))
