from requests import post
from argparse import ArgumentParser
import json

DEFAULT_MSG = 'Hello, TestBot.'
BASEURL = 'http://127.0.0.1:5002'
BOTS = [
    {
        'type': 'sportsengine',
        'url': '/testbot'
    },
    {
        'type': 'pointstreak',
        'url': '/psbot'
    },
    {
        'type': 'dash',
        'url': '/dashbot'
    }
]
parser = ArgumentParser()
parser.add_argument("-m", "--message", dest="msg", default=DEFAULT_MSG)
args = parser.parse_args()
test_data = {
    'attachments': [],
    'avatar_url': 'https://i.groupme.com/123456789',
    'created_at': 1302623328,
    'group_id': '1234567890',
    'id': '1234567890',
    'name': 'John',
    'sender_id': '12345',
    'sender_type': 'user',
    'source_guid': 'GUID',
    'system': False,
    'text': args.msg,
    'user_id': '1234567890'
}
for bot in BOTS:
    print "==== {0} ====".format(bot['type'])
    post('{}{}'.format(BASEURL, bot['url']), data=json.dumps(test_data))
    print ""
