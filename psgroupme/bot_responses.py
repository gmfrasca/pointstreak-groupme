# Responses shared by all bots
GLOBAL_RESPONSES = [
    {
        'input': r'(hi|hello|greetings|salutations|sup),? {bot_name}',
        'reply': 'Hello, {name}'
    },
    {
        'input': r'show me the (source|sauce|src|code)',
        'reply': ('You can find it at ' +
                  'https://github.com/gmfrasca/pointstreak-groupme')
    }
]

# Responses specific to ScheduleBot
SCHEDULE_BOT_RESPONSES = []
