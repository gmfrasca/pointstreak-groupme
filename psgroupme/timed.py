from timed_bots import GamedayReminderBot
import signal


def main():
    bots_to_run = [GamedayReminderBot]
    running_bots = []
    for bot_class in bots_to_run:
        bot = bot_class()
        bot.start()
        running_bots.append(bot)

    while True:
        try:
            signal.pause()
        except KeyboardInterrupt:
            for bot in running_bots:
                bot.stop()
            exit(0)
if __name__ == '__main__':
    main()
