from requests import post
from argparse import ArgumentParser
import json

parser = ArgumentParser()
parser.add_argument("-u", "--url", dest="url", required=True)
args = parser.parse_args()
test_data={
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
    'text': 'Hello, TestBot',
    'user_id': '1234567890'
}
post(args.url, data=json.dumps(test_data))


