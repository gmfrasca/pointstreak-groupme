from flask import Flask
from flask_restful import Api
from config_manager import ConfigManager
import sys
import logging
import bots  # noqa: need this to subclass


def str_to_class(class_name):
    return reduce(getattr, class_name.split("."), sys.modules[__name__])


def main():
    """Start up a Flask REST API Frontend"""
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
        subclass_name = "{0}{1}".format(class_name, bot_id)
        bot_class = str_to_class(class_name)
        logging.info("Adding {0}".format(subclass_name))
        bot.update(dict(img_cfg=img_cfg, public_url=public_url))
        api.add_resource(type(subclass_name, (bot_class,), {}), bot_url,
                         resource_class_kwargs=dict(bot_cfg=bot))

    # Start up the REST API
    app.run(host='0.0.0.0', port=cm.get_flask_port())


if __name__ == '__main__':
    main()
