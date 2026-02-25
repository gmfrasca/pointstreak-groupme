from psgroupme.config_manager import ConfigManager
from psgroupme.interfaces.responder import ResponderFactory
from functools import reduce
import signal
import sys
import logging
import psgroupme.bots as bots# noqa


TIMED_BOT_CFG = 'config/timed.local.yaml'


def str_to_class(class_name):
    return reduce(getattr, class_name.split("."), sys.modules[__name__])


def main(cfg_path=TIMED_BOT_CFG):
    logger = logging.getLogger("TimedBotManager")
    cm = ConfigManager(cfg_path=cfg_path)
    running_bots = []
    for bot_cfg in cm.get_bots():
        class_name = bot_cfg.get('class_name')
        bot_class = str_to_class(class_name)

        default_responder_cfg = dict(type='groupme')
        responder_cfg = bot_cfg.get('responders', [default_responder_cfg])
        for rcfg in responder_cfg:
            if 'bot_id' not in rcfg:
                rcfg['bot_id'] = bot_cfg.get('bot_id')
            responder_type = rcfg.get('type', 'groupme')
            responder = ResponderFactory().get_responder(responder_type, **rcfg)

            logger.info("Adding {0}".format(class_name))
            bot = bot_class(responder=responder, **bot_cfg)
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
