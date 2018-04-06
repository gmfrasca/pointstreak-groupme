import yaml

RESPONSE_YAML = 'config/responses.local.yaml'


class BotResponseManager(object):

    def __init__(self, cfg_path=RESPONSE_YAML):
        self.cfg_path = cfg_path
        self.reload_data()

    def reload_data(self):
        with open(self.cfg_path) as f:
            self.data = yaml.load(f)

    def get(self, key, default=None):
        self.reload_data()
        return self.data.get(key, default)

    def get_extra_context(self):
        return self.get('extra_context', dict())

    def get_responses(self):
        return self.get('responses', dict())

    def get_global_responses(self):
        return self.get_responses().get('global', list())
