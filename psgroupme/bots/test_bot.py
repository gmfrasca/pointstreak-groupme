from hockey_bot import HockeyBot
import logging
import sys


class TestBot(HockeyBot):
    """Debug"""
    def respond(self, msg):
        """Respond using the matched message reply"""
        logging.info("Response: {0}".format(msg))
        print(msg)


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
