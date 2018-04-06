import yaml

# # Responses shared by all bots
# # TODO: Delete the blocks
# github_url = 'https://github.com/gmfrasca/pointstreak-groupme'
# GLOBAL_RESPONSES = [
#     {
#         'input': r'(hi|hello|greetings|salutations|sup),? {bot_name}',
#         'reply': 'Hello, {name}'
#     },
#     {
#         'input': r'show me the (source|sauce|src|code)',
#         'reply': 'You can find it at ' + github_url
#     },
#     {
#         'input': r'(what|who) is {bot_name}',
#         'reply': ('I am a GroupMe helper bot, beep boop.\n' +
#                   'More info at ' + github_url)
#     }
# ]
#
# # Responses specific to ScheduleBot
# SCHEDULE_BOT_RESPONSES = []

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
