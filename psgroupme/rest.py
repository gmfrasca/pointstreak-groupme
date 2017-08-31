from flask import Flask
from flask_restful import Api
import bots

app = Flask(__name__)
api = Api(app)
api.add_resource(bots.ScheduleBot, '/schedulebot')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
