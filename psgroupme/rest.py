from flask import Flask
from flask_restful import Api
import bots


def main():
    # Setup the Flask App
    app = Flask(__name__)
    api = Api(app)

    # Add Bots to a REST API URL here
    api.add_resource(bots.ScheduleBot, '/schedulebot')

    # Start up the REST API
    app.run(host='0.0.0.0', port='5002')


if __name__ == '__main__':
    main()
