# Responses shared by all bots
github_url = 'https://github.com/gmfrasca/pointstreak-groupme'

GLOBAL_RESPONSES = [
    {
        'input': r'(hi|hello|greetings|salutations|sup),? {bot_name}',
        'reply': 'Hello, {name}'
    },
    {
        'input': r'show me the (source|sauce|src|code)',
        'reply': 'You can find it at ' + github_url

    },
    {
        'input': r'(what|who) is {bot_name}',
        'reply': ('I am a GroupMe helper bot, beep boop.\n' +
                  'More info at ' + github_url)
    }
]

# Responses specific to ScheduleBot
SCHEDULE_BOT_RESPONSES = []
