import requests
import json
import re

DEFAULT_TLR_URL = 'https://teamlockerroom.com'


class TeamLockerRoom(object):

    def __init__(self, username, password, url=DEFAULT_TLR_URL):
        self.baseurl = url
        self.session = requests.session()
        self.username = username
        self.password = password
        self.login()

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

    def get_next_game_attendance(self):
        next_game = self.get_next_game()
        if next_game:
            attin = next_game.get('attin', '0')
            attout = next_game.get('attout', '0')
            return ("There are {0} players checked in, " +
                    "and {1} players checked out").format(attin, attout)
        return "No upcoming games found."


def main():
    tlr = TeamLockerRoom('<EMAIL_HERE>', '<PASSWORD_HERE>')
    print tlr.get_next_game_attendance()


if __name__ == '__main__':
    main()
