from master_bot import MasterBot
import sys


class TestBot(MasterBot):
    """Debug"""

    def __init__(self, *args, **kwargs):
        super(TestBot, self).__init__(*args, **kwargs)
        self.responder.live = False


def main(argv):
    msg_text = 'what is today'
    if len(argv) > 1:
        msg_text = argv[1]
    test = TestBot()
    test_msg = {
        'attachments': [],
        'avatar_url': 'http://example.com',
        'created_at': 1234567890,
        'group_id': '1234567890',
        'id': '1234567890',
        'name': 'foobar',
        'sender_id': '12345',
        'sender_type': 'user',
        'source_guid': 'GUID',
        'system': False,
        'text': msg_text,
        'user_id': '1234567890'
    }
    test.handle_msg(test_msg)


if __name__ == '__main__':
    main(sys.argv)
