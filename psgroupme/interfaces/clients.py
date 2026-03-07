from flask import Flask
from flask_restful import Api
from psgroupme.config_manager import ConfigManager
from psgroupme.interfaces.listener import GroupmeListener, DiscordListener
from functools import reduce
import sys
import logging
import psgroupme.bots as bots # noqa: need this to subclass
import _thread
from time import sleep
import discord
import asyncio


class ClientManager(object):
    def __init__(self, config_path):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.cm = ConfigManager(config_path)
        self.fcm = FlaskClientManager(config_path)
        if self.cm.get_discord_token() is not None:
            self.dcm = DiscordClientManager(config_path)
        else:
            self._logger.warning("Discord token is not set, cannot set up Discord client. Will not be available.")
            self.dcm = None
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
                self.add_listener(l, bot,bot_url)
    
    def add_listener(self, listener_cfg, bot, bot_url):
        listener_type = listener_cfg.get('type', 'groupme')
        if listener_type == 'groupme':
            bot_url = listener_cfg.get('url', bot_url)
            if bot_url is not None:
                self._logger.info("Adding Groupme listener for bot {} at {}".format(bot.bot_name, bot_url))
                self.fcm.add_bot(GroupmeListener, bot_url, {'bot': bot})
            else:
                self._logger.warning("Bot URL is not set, cannot add Groupme listener")
        elif listener_type == 'discord':
            if self.dcm is None:
                self._logger.warning("Discord client is not available, cannot add Discord listener")
                return
            channel_id = listener_cfg.get('channel_id', None)
            if channel_id is not None:
                self._logger.info("Adding Discord listener for bot {} at channel {}".format(bot.bot_name, channel_id))
                self.dcm.add_listener(DiscordListener(bot, channel_id))
            else:
                self._logger.warning("Channel ID is not set, cannot add Discord listener")
        else:
            self._logger.warning("Unknown listener type '{0}', bot will not have a listener".format(listener_type))

    def run(self):
        client_threads = {'flask': self.fcm.run}

        # Add Discord client if it is available
        if self.dcm is not None:
            client_threads['discord'] = self.dcm.run

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

# TODO: Right now we only support one discord client (ie one token)
# TODO: We should support indefinate numbers of clients managed by a single controller
class DiscordClientManager(object):

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path):
        if self._initialized:
            # Already initialized
            return

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info("Setting up Discord client")
        self.cm = ConfigManager(config_path)
        self.token = self.cm.get_discord_token()
        if self.token is None:
            self._logger.warning("Discord token is not set, cannot set up Discord client. Will not be available.")
            self.discord_client = None
            return
        intents = discord.Intents.default()
        intents.message_content = True
        discord_client = discord.Client(intents=intents)
        self.discord_client = discord_client
        self.listeners = []
        self._initialized = True

        @discord_client.event
        async def on_ready():
            self._logger.info("Discord client ready")

        @discord_client.event
        async def on_message(message):
            channel_id = message.channel.id
            self._logger.debug(f"Message received in channel {message.channel.name} (id: {channel_id}): {message.content}")
            for listener in self.listeners:
                if listener.channel_id == channel_id:
                    self._logger.debug(f"Recieved Message for bot {listener.bot.bot_name}: {message.content}")
                    listener.process_message(message)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def send(self, channel_id, message):
        async def _send(channel_id, message):
            channel = self.discord_client.get_channel(channel_id)
            try:
                await channel.send(message)
                self._logger.info("Message sent to channel {}: {}".format(channel.name, message))
                return True
            except Exception as e:
                self._logger.error("Error sending message to channel {}: {}".format(channel.name, e))
                return False
        asyncio.run_coroutine_threadsafe(_send(channel_id, message), self.discord_client.loop)

    def get_client(self):
        return self.discord_client

    def run(self):
        self._logger.info("Running Discord client")
        self.discord_client.run(self.token)


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
