from flask import Flask
from flask_restful import Api
from psgroupme.config_manager import ConfigManager
from psgroupme.interfaces.responder import ResponderFactory
from psgroupme.interfaces.listener import GroupmeListener
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
    for bot_cfg in cm.get_bots():
        class_name = bot_cfg.get('class_name')
        bot_class = str_to_class(class_name)

        # Handle Legacy configuration options
        bot_url = bot_cfg.get('bot_url')
        bot = bot_class(bot_cfg=bot_cfg)

        # Set up listeners
        listeners_cfg = bot_cfg.pop('listeners', [])
        for l in listeners_cfg:
            listener_type = l.get('type', 'groupme')
            if listener_type == 'groupme':
                bot_url = l.get('url', bot_url)
                if bot_url is not None:
                    api.add_resource(GroupmeListener, bot_url, resource_class_kwargs={'bot': bot})
                else:
                    logger.warning("Bot URL is not set, cannot add Groupme listener")
            else:
                logger.warning("Unknown listener type '{0}', bot will not have a listener".format(listener_type))

    # Start up the REST API
    app.run(host='0.0.0.0', port=cm.get_flask_port())


if __name__ == '__main__':
    main()
