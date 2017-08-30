from flask import Flask
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

class ScheduleAPI(Resource):
    def get(self):
        return {'foo': 'bar'}

api.add_resource(ScheduleAPI, '/schedule')

if __name__ == '__main__':
    app.run(port='5002')


