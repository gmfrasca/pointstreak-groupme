from flask import Flask
from flask_restful import Api
from psgroupme.config_manager import ConfigManager
from psgroupme.interfaces.responder import ResponderFactory
from functools import reduce
import sys
import logging
import psgroupme.bots as bots # noqa: need this to subclass


def str_to_class(class_name):
    return reduce(getattr, class_name.split("."), sys.modules[__name__])


def main():
    """Start up a Flask REST API Frontend"""
    logger = logging.getLogger("FlaskBotManager")
    cm = ConfigManager()

    # Setup Path for File server
    img_cfg = cm.get_img_server_config()
    public_url = cm.get_public_url()

    # Setup the Flask App
    app = Flask(__name__, static_folder=img_cfg.get('path'),
                static_url_path=img_cfg.get('dest'))
    api = Api(app)

    # Add Bots to a REST API URL here
    for bot in cm.get_bots():
        class_name = bot.get('class_name')
        bot_id = bot.get('bot_id')
        bot_url = bot.get('bot_url')
        default_bot_cfg = {"bot_id": bot_id, "type": "groupme"}

        responders_cfg = bot.get('responders', [default_bot_cfg])
        responders = []
        for rcfg in responders_cfg:
            responder_type = rcfg.get('type', 'groupme')
            if 'bot_id' not in rcfg:
                rcfg['bot_id'] = bot_id
            if 'bot_url' not in rcfg:
                rcfg['bot_url'] = bot_url
            responders.append(ResponderFactory().get_responder(responder_type, **rcfg))

        # Determine the bot class
        bot_class = str_to_class(class_name)

        # Stand up the various listeners for each responder used by this bot
        for r in responders:
            # Generate bot config for this responder
            bot_cfg = bot.copy()
            bot_cfg.update(dict(
                bot_id=r.bot_id,
                bot_url=r.bot_url,
                img_cfg=img_cfg,
                public_url=public_url))
            bot_name = "{0}-{1}".format(class_name, r.bot_id)
            logger.info(f"Adding {bot_name}")

            # Add a Flask listener for this responder if it is a Groupme responder and has a bot_url
            if r.host_type == 'flask' and r.bot_url is not None:
                logger.info(f"Adding Flask listener for {r.bot_id} on endpoint {r.bot_url}")
                resource_class = type(bot_name, (bot_class,), {})
                api.add_resource(resource_class, r.bot_url, resource_class_kwargs=dict(bot_cfg=bot_cfg, responder=r))
            else:
                logger.warning("Responder type '{0}' has no host type, bot will not have a listener".format(r.host_type))

    # Start up the REST API
    app.run(host='0.0.0.0', port=cm.get_flask_port())


if __name__ == '__main__':
    main()
