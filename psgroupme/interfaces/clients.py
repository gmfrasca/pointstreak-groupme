from flask import Flask
from flask_restful import Api
from psgroupme.config_manager import ConfigManager
from psgroupme.interfaces.listener import GroupmeListener
from functools import reduce
import sys
import logging
import psgroupme.bots as bots # noqa: need this to subclass
import _thread
from time import sleep

class ClientManager(object):
    def __init__(self, config_path):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.cm = ConfigManager(config_path)
        self.fcm = FlaskClientManager(config_path)
        self.create_bots()

    def str_to_class(self, class_name):
        return reduce(getattr, class_name.split("."), sys.modules[__name__])

    def create_bots(self):
        for bot_cfg in self.cm.get_bots():
            class_name = bot_cfg.get('class_name')
            bot_class = self.str_to_class(class_name)

            # Handle Legacy configuration options
            bot_url = bot_cfg.get('bot_url')
            default_listener_cfg = {"type": "groupme", "url": bot_url}

            # Create bot
            bot = bot_class(bot_cfg=bot_cfg)

            # Set up listeners
            listeners_cfg = bot_cfg.pop('listeners', [default_listener_cfg])
            for l in listeners_cfg:
                self.add_listener(bot, l, bot_url)
    
    def add_listener(self, bot, listener_cfg, bot_url):
        listener_type = listener_cfg.get('type', 'groupme')
        if listener_type == 'groupme':
            bot_url = listener_cfg.get('url', bot_url)
            if bot_url is not None:
                self._logger.info("Adding Groupme listener for bot {} at {}".format(bot.bot_name, bot_url))
                self.fcm.add_bot(GroupmeListener, bot_url, {'bot': bot})
            else:
                self._logger.warning("Bot URL is not set, cannot add Groupme listener")
        else:
            self._logger.warning("Unknown listener type '{0}', bot will not have a listener".format(listener_type))

    def run(self):
        client_threads = {
            'flask': self.fcm.run,
        }

        for thread_name, thread_func in client_threads.items():
            try:
                _thread.start_new_thread(thread_func, ())
            except Exception as e:
                logging.error("Unable to start {} thread".format(thread_name))
                logging.error(e)

        running = True
        while running:
            try:
                sleep(1)
            except KeyboardInterrupt:
                running = False


class FlaskClientManager(object):
    def __init__(self, config_path):
        self.cm = ConfigManager(config_path)
        self.img_cfg = self.cm.get_img_server_config()
        self.host = '0.0.0.0'
        self.port = self.cm.get_flask_port()

        self.app = Flask(__name__,
                         static_folder=self.img_cfg.get('path'),
                         static_url_path=self.img_cfg.get('dest'))
        self.api = Api(self.app)

    def add_bot(self, bot_class, bot_url, bot_kwargs):
        self.api.add_resource(bot_class, bot_url, resource_class_kwargs=bot_kwargs)

    def run(self):
        self.app.run(host=self.host, port=self.port)




def main():
    """Start up a Client Manager"""
    client_manager = ClientManager(config_path=None)
    client_manager.run()


if __name__ == '__main__':
    main()
