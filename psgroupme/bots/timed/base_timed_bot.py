from psgroupme.interfaces.responder import Responder
import threading
import logging


class BaseTimedBot(threading.Thread):

    def __init__(self, **kwargs):
        """Load the config for this bot based on Name"""
        super(BaseTimedBot, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stop_event = threading.Event()
        self.daemon = True
        self.bot_id = kwargs.get('bot_id')
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)

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
            self.responder.reply(msg)
