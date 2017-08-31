from team_schedule import PointstreakSchedule

# Responses shared by all bots
GLOBAL_RESPONSES = [
    {
        'input': r'(hi|hello|(wha[tz]s?\s?up)), {bot_name}',
        'reply': 'Hello, {name}'
    }
]

# Responses specific to ScheduleBot
sched = PointstreakSchedule()
SCHEDULE_BOT_RESPONSES = [
    {
        'input': r'when.*next game\??',
        'reply': str(sched.get_next_game())
    },
    {
        'input': r'what was the score',
        'reply': str(sched.get_last_game())
    },
    {
        'input': r'how( did)? we do',
        'reply': str(sched.get_last_game())
    },
    {
        'input': r'what is.*schedule',
        'reply': str(sched)
    }
]
