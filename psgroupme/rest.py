from flask import Flask
from flask_restful import Api
import bots


def main():
    """Start up a Flask REST API Frontent"""
    local = False

    # Setup the Flask App
    app = Flask(__name__)
    api = Api(app)

    # Add Bots to a REST API URL here
    if local:
        api.add_resource(bots.TestBot, '/testbot')
    else:
        api.add_resource(bots.ScheduleBot, '/schedulebot')
        api.add_resource(bots.HockeyBot, '/hockeybot')

    # Start up the REST API
    app.run(host='0.0.0.0', port='5002')


if __name__ == '__main__':
    main()
