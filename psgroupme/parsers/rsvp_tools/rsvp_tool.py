import requests
import logging
import sys


class RsvpTool(object):

    DEFAULT_URL = 'https://teamlockerroom.com'

    def __init__(self, username, password, url=DEFAULT_URL):
        self.baseurl = url
        self.session = requests.session()
        self.username = username
        self.password = password
        self.login()

    def login(self):
        pass

    # TODO: Refactor to get_next_game_attendance_str
    def get_next_game_attendance(self):
        return 'NextGameAttendanceStr'

    def get_next_game_attendees(self):
        return 'NextGameAttendees'

    def try_checkin(self, name, status):
        print("NOTIMPLEMENTED")

    def get_next_game_lines(self):
        print("NOTIMPLEMENTED")

    def get_team_fee_progress(self):
        print("NOTIMPLEMENTED")


def main():
    assert len(sys.argv) > 2
    tlr = RsvpTool(sys.argv[1], sys.argv[2])
    logging.debug(tlr.get_next_game_attendees())
    logging.debug(tlr.get_next_game_attendance())


if __name__ == '__main__':
    main()
