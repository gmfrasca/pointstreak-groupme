from rsvp_tool import RsvpTool
import logging
import json
import sys
import re


DEFAULT_URL = 'https://teamlockerroom.com'


class TeamLockerRoom(RsvpTool):

    def __init__(self, username, password):
        super(TeamLockerRoom, self).__init__(username, password, DEFAULT_URL)

    def get_csrf_token(self):
        response = self.session.get(self.baseurl)
        match = re.search('var csrf = \"\S+\"', response.text)
        if match:
            match = re.search('\"\S+\"', match.group(0)).group(0)
            return match.replace('"', '')
        raise RuntimeError("Could not parse csrf token from source")

    def login(self):
        csrf = self.get_csrf_token()
        payload = {
            "username": self.username,
            "password": self.password,
        }
        headers = {
            "X-CSRF-Token": csrf,
        }
        self.session.post(
            self.baseurl + "/session/login",
            headers=headers,
            data=payload)

    @property
    def schedule(self):
        self.login()
        response = self.session.get(self.baseurl + "/#home")
        match = re.search('tlr.teamschedule = [^\n]*', response.text)
        if not match:
            return dict()
        match = re.search("'[^\n]*'", match.group(0))
        schedule = match.group(0).replace('&quot;', '"')
        schedule = schedule.strip().strip(';').strip("'")
        schedule.replace("}", "}\n")
        return json.loads(schedule)

    def get_next_game(self):
        for game in self.schedule:
            played = game.get('played', -1)
            if played and int(played) == 0:
                return game
        return None

    # TODO: Refactor to get_next_game_attendance_str
    def get_next_game_attendance(self):
        next_game = self.get_next_game()
        if next_game:
            attin = next_game.get('attin', '0')
            attout = next_game.get('attout', '0')
            return ("There are {0} players checked in, " +
                    "and {1} players checked out").format(attin, attout)
        return "No upcoming games found."

    def get_next_game_id(self):
        game = self.get_next_game()
        if game:
            return game.get('gameid', None)
        return None

    def get_game_attendees(self, gameid):
        game = self.get_next_game()
        game_url = '{0}/#game/{1}'.format(self.baseurl, game.get('gameid'))

        # FIXME DEBUG
        game_url = 'https://teamlockerroom.com/#game/3139016'
        payload = {
            'status-17768537': 'out',
            'flags-17768537': 'foobar'
        }
        response = self.session.post(game_url, data=payload)
        logging.info(response.text)

        return game_url

    def get_next_game_attendees(self):
        gameid = self.get_next_game_id()
        return self.get_game_attendees(gameid) if gameid else None


def main():
    assert len(sys.argv) > 2
    tlr = TeamLockerRoom(sys.argv[1], sys.argv[2])
    logging.debug(tlr.get_next_game_attendees())
    logging.debug(tlr.get_next_game_attendance())


if __name__ == '__main__':
    main()
