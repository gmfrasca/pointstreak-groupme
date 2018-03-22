from flask import Flask
from flask_restful import Api
from config_manager import ConfigManager
import bots
import sys


def str_to_class(class_name):
    return reduce(getattr, class_name.split("."), sys.modules[__name__])


def main():
    """Start up a Flask REST API Frontent"""
    local = False

    # Setup the Flask App
    app = Flask(__name__)
    api = Api(app)

    # Add Bots to a REST API URL here
    if local:
        api.add_resource(bots.TestBot, '/testbot')
        api.add_resource(type('SubTestBot', (bots.TestBot,), {}), '/doublebot')
    else:
        cm = ConfigManager()
        for bot in cm.get_bots():
            class_name = bot.get('class_name')
            bot_id = bot.get('bot_id')
            bot_url = bot.get('bot_url')
            subclass_name = "{0}{1}".format(class_name, bot_id)
            bot_class = str_to_class(class_name)
            print("Adding {0}".format(subclass_name))
            api.add_resource(type(subclass_name, (bot_class,), {}), bot_url,
                             resource_class_kwargs=dict(bot_id=bot_id))

    # Start up the REST API
    app.run(host='0.0.0.0', port='5002')


if __name__ == '__main__':
    main()
