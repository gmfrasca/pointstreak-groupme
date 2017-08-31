import yaml

DEFAULT_CONFIG = '../config/bots.local.yaml'


class ConfigManager(object):

    def __init__(self, cfg_path=DEFAULT_CONFIG):
        self.cfg = self.load_cfg(cfg_path)

    def load_cfg(self, cfg_path):
        with open(cfg_path) as f:
            return yaml.load(f)

    def get_bot_data(self, bot_name):
        matched_bots = [bot for bot in self.cfg['bots'] if
                        bot['bot_name'] == bot_name]
        if len(matched_bots) > 0:
            return matched_bots[0]
        return None

    def get_bot_id(self, bot_name):
        bot = self.get_bot_data(bot_name)
        return bot.get('bot_id', None) if bot else None
