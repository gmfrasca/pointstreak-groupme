from bs4 import BeautifulSoup
from rsvp_tool import RsvpTool
import logging
import requests
import sys
import re


DEFAULT_URL = 'https://benchapp.com'
LOGIN_URL = '/player-area/ajax/login.php'
NEXT_GAME_URL = '/schedule/next-event'
CHECKIN_URL = '/schedule-area/ajax/setAttendance.php'


class CheckinException(Exception):
    pass


class BenchApp(RsvpTool):

    def __init__(self, username, password):
        super(BenchApp, self).__init__(username, password, DEFAULT_URL)
        self.retrieve_next_game_page()

    def login(self):
        data = dict(email=self.username, password=self.password)
        self.session.post("{0}{1}".format(self.baseurl, LOGIN_URL),
                          data=data)

    def parse_playeritem(self, playeritem):
        text = playeritem.findAll("a", {"href": "#profile"})[0]
        date = text.small
        name = date.previous_sibling
        return name, date

    @property
    def has_upcoming_game(self):
        page = self.get_next_game_page().text
        soup = BeautifulSoup(page, 'html.parser')
        no_results_div = soup.find_all("div", {"class": "noResults"})
        if len(no_results_div) == 0:
            return True
        return False

    def get_next_game_page(self):
        return self.next_game

    def retrieve_next_game_page(self):
        self.next_game = self.session.get('{0}{1}'.format(self.baseurl,
                                                          NEXT_GAME_URL))

    def get_next_game_data(self):
        if self.has_upcoming_game is False:
            return dict()
        page = self.get_next_game_page().text
        soup = BeautifulSoup(page, 'html.parser')
        in_count = soup.find("div", {"class": "inCount"}).text
        out_count = soup.find("div", {"class": "outCount"}).text
        data = dict(in_count=in_count, out_count=out_count)
        for checkin_type in ['attending', 'notAttending',
                             'waitlist', 'unknown']:
            players = soup.find("ul", {"id": checkin_type})
            playeritems = players.findAll("li", {"class": "playerItem"})
            player_list = list()
            for playeritem in playeritems:
                player, date = self.parse_playeritem(playeritem)
                player_list.append(dict(player=player, date=date))
            data.update({checkin_type: player_list})
        return data

    def get_list_of_player_names(self, list_type):
        data = self.get_next_game_data()
        player_list = data.get(list_type, list())
        names = list()
        for player in player_list:
            names.append(player.get('player', None).strip().encode('ascii',
                                                                   'ignore'))
        return names

    def get_list_of_attending_players(self):
        return self.get_list_of_player_names('attending')

    def get_list_of_not_attending_players(self):
        return self.get_list_of_player_names('notAttending')

    def get_list_of_waitlisted_players(self):
        return self.get_list_of_player_names('waitlist')

    def get_list_of_unknown_status_players(self):
        return self.get_list_of_player_names('unknown')

    def get_number_checked_in(self):
        return self.get_next_game_data().get('in_count', 0)

    def get_number_checked_out(self):
        return self.get_next_game_data().get('out_count', 0)

    def get_number_waitlisted(self):
        return len(self.get_list_of_waitlisted_players())

    def get_number_of_unknown_status_players(self):
        return len(self.get_list_of_unknown_status_players())

    def get_next_game_attendance(self):
        self.retrieve_next_game_page()
        if self.has_upcoming_game:
            return "In: {0}, Out: {1}, Waitlist: {2}, No Status: {3}".format(
                self.get_number_checked_in(),
                self.get_number_checked_out(),
                self.get_number_waitlisted(),
                self.get_number_of_unknown_status_players())
        else:
            return "No upcoming games found."

    def get_next_game_attendees(self):
        self.retrieve_next_game_page()
        if self.has_upcoming_game:
            in_list = self.get_list_of_attending_players()
            out_list = self.get_list_of_not_attending_players()
            wait_list = self.get_list_of_waitlisted_players()
            unkn_list = self.get_list_of_unknown_status_players()
            in_str = reduce((lambda x, y: '{0}, {1}'.format(x, y)), in_list) \
                if len(in_list) > 0 else "None"
            out_str = reduce((lambda x, y: '{0}, {1}'.format(x, y)),
                             out_list) if len(out_list) > 0 else "None"
            wait_str = reduce((lambda x, y: '{0}, {1}'.format(x, y)),
                              wait_list) if len(wait_list) > 0 else "None"
            unkn_str = reduce((lambda x, y: '{0}, {1}'.format(x, y)),
                              unkn_list) if len(unkn_list) > 0 else "None"
            return "In: {0}, Out: {1}, Waitlist: {2}, No Status: {3}".format(
                in_str, out_str, wait_str, unkn_str)
        else:
            return "No upcoming games found."

    def try_checkin(self, name, status='in'):
        if self.has_upcoming_game is False:
            return
        page = self.get_next_game_page().text
        soup = BeautifulSoup(page, 'html.parser')
        players = soup.find_all('li',
                                id=lambda x: x and x.startswith('player-'))
        found = False
        playeritem = None
        for player in players:
            # Checkin By ID, exact match
            if player.get('id').endswith(name) or \
                    re.search(name.lower(), player.text.lower()) is not None:
                # Multiple results, too ambigous so can't continue
                if found:
                    raise CheckinException(
                        "Multiple Players with name same name found")
                else:
                    found = True
                    playeritem = player
        if found:
            try:
                checkin = playeritem.find("a", {"href": "#IN"})
                checkin_fn = checkin.get('onclick', '')
                params = checkin_fn.split(';')[0].split(')')[0].split('(')[1]
                (teamID, seasonID, gameID, gameKey, playerID,
                 ignore, refresh) = params.split(',')
                data = dict(teamID=int(teamID),
                            gameID=int(gameID),
                            seasonID=int(seasonID),
                            playerID=int(playerID),
                            status=str(status),
                            gameKey=gameKey.encode('ascii',
                                                   'ignore').strip("'"))
                requests.get('{0}{1}'.format(DEFAULT_URL, CHECKIN_URL),
                             params=data)
            except:
                raise CheckinException(
                    "ERROR::Could not check in {0}".format(name))


def main():
    assert len(sys.argv) > 2
    ba = BenchApp(sys.argv[1], sys.argv[2])
    logging.debug(ba.get_next_game_attendees())
    logging.debug(ba.get_next_game_attendance())


if __name__ == '__main__':
    main()
