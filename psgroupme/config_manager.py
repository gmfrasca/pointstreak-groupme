import yaml
import os

CONFIG_PATH = 'config/bots.local.yaml'
PACKAGE_PATH = os.path.dirname(os.path.dirname(__file__))
DEFAULT_CONFIG = os.path.join(PACKAGE_PATH, CONFIG_PATH)
IMG_PATH = os.path.join(PACKAGE_PATH, 'img')
DEFAULT_FLASK_PORT = 5002


class ConfigManager(object):

    def __init__(self, cfg_path=DEFAULT_CONFIG):
        """Load the groupme bot config"""
        # Handle NoneType cfg_path
        cfg_path = cfg_path if cfg_path else DEFAULT_CONFIG
        self.cfg = self.load_cfg(cfg_path)

    def load_cfg(self, cfg_path):
        """Load the config from a target YAML"""
        with open(cfg_path) as f:
            return yaml.load(f)

    def get_bot_data(self, bot_name):
        """Get the configuration for a bot based on bot name"""
        matched_bots = [bot for bot in self.cfg['bots'] if
                        bot['class_name'] == bot_name]
        if len(matched_bots) > 0:
            return matched_bots[0]
        return dict()

    def get_bot_id(self, bot_name):
        """Get the bot id for a target bot given it's name"""
        bot = self.get_bot_data(bot_name)
        return bot.get('bot_id', None) if bot else None

    def get_bot_data_by_id(self, bot_id):
        """Get the configuration for a bot based on bot id"""
        matched_bots = [bot for bot in self.cfg['bots'] if
                        bot['bot_id'] == bot_id]
        return matched_bots[0] if len(matched_bots) > 0 else dict()

    def get_bots(self):
        """Get list of bot configs"""
        return self.cfg.get('bots', list())

    def get_flask_port(self):
        if 'flask' in self.cfg:
            return self.cfg['flask'].get('port', DEFAULT_FLASK_PORT)
        return DEFAULT_FLASK_PORT

    def get_img_server_config(self):
        return dict(path=self.cfg.get('img', dict()).get('path', IMG_PATH),
                    dest=self.cfg.get('img', dict()).get('dest', '/img'))

    def get_public_url(self):
        return self.cfg.get('public_url', 'http://localhost:5000')
