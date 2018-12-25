from bs4 import BeautifulSoup
from rsvp_tool import RsvpTool
from re import sub
from decimal import Decimal
import logging
import sys
import re


DEFAULT_URL = 'https://benchapp.com'
LOGIN_URL = '/player-area/ajax/login.php'
NEXT_GAME_URL = '/schedule/next-event'
CHECKIN_URL = '/schedule-area/ajax/setAttendance.php'
FINANCES_URL = '/team/finances/fees/index.html'

PROGRESS_BAR_CHARS = 20


class CheckinException(Exception):
    pass


class BenchApp(RsvpTool):

    def __init__(self, username, password, **kwargs):
        super(BenchApp, self).__init__(username, password, DEFAULT_URL,
                                       **kwargs)
        self.next_game_data = None
        self.retrieve_next_game_page()
        self.retrieve_finances_page()

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
        return len(no_results_div) == 0

    def get_next_game_page(self):
        return self.next_game

    def retrieve_next_game_page(self):
        self.next_game = self.session.get('{0}{1}'.format(self.baseurl,
                                                          NEXT_GAME_URL))

    def retrieve_finances_page(self):
        self.finances = self.session.get('{0}{1}'.format(self.baseurl,
                                                         FINANCES_URL))

    def get_finances_page(self):
        return self.finances

    def get_next_game_data(self):
        if self.next_game_data is not None:
            return self.next_game_data
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
        self.next_game_data = data
        return data

    def moneytext_to_float(self, moneytext):
        return float(Decimal(sub(r'[^\d.-]', '', moneytext)))

    def get_team_fee_progress(self):
        page = self.get_finances_page().text
        soup = BeautifulSoup(page, 'html.parser')
        rosterlist = soup.find("table", {"id": "rosterList"})
        footer = rosterlist.find("tfoot")
        items = footer.find_all("td")

        paid = self.moneytext_to_float(items[2].text)
        fee = self.moneytext_to_float(items[1].text)

        # Do calculations here
        percent = 1.0
        try:
            percent = paid / fee
        except ZeroDivisionError:
            pass
        num_x = int(PROGRESS_BAR_CHARS * percent)
        num_rem = PROGRESS_BAR_CHARS - num_x
        x_string = '#' * num_x
        rem_string = '-' * num_rem
        return "[{}{}] {:.2f}%\r\n (${:.2f} / ${:.2f})".format(
            x_string, rem_string, 100 * percent, paid, fee)

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
        if self.has_upcoming_game:
            return "In: {0}, Out: {1}, Waitlist: {2}, No Status: {3}".format(
                self.get_number_checked_in(),
                self.get_number_checked_out(),
                self.get_number_waitlisted(),
                self.get_number_of_unknown_status_players())
        else:
            return "No upcoming games found."

    def get_next_game_attendees(self):
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
            return ("In: {0}\r\nOut: {1}\r\nWaitlist: {2}" +
                    "\r\nNo Status: {3}").format(in_str, out_str,
                                                 wait_str, unkn_str)
        else:
            return "No upcoming games found."

    def get_next_game_lines(self):
        if self.has_upcoming_game is False:
            return "No upcoming games found."
        page = self.get_next_game_page().text
        soup = BeautifulSoup(page, 'html.parser')
        controls = soup.find('div', {'class': 'mainControls'}).find_all('a')
        line_url = None
        for control in controls:
            line_url = control.get('href') if \
                control.get('href').startswith('/schedule/lines') else line_url
        response = self.session.get('{0}{1}'.format(self.baseurl, line_url))
        soup = BeautifulSoup(response.text, 'html.parser')
        lines = {
            'forwards': [
                {
                    'leftwing': self.get_player_in_line_pos(soup, 'fl1-lw'),
                    'center': self.get_player_in_line_pos(soup, 'fl1-c'),
                    'rightwing': self.get_player_in_line_pos(soup, 'fl1-rw')
                },
                {
                    'leftwing': self.get_player_in_line_pos(soup, 'fl2-lw'),
                    'center': self.get_player_in_line_pos(soup, 'fl2-c'),
                    'rightwing': self.get_player_in_line_pos(soup, 'fl2-rw')
                },
                {
                    'leftwing': self.get_player_in_line_pos(soup, 'fl3-lw'),
                    'center': self.get_player_in_line_pos(soup, 'fl3-c'),
                    'rightwing': self.get_player_in_line_pos(soup, 'fl3-rw')
                },
                {
                    'leftwing': self.get_player_in_line_pos(soup, 'fl4-lw'),
                    'center': self.get_player_in_line_pos(soup, 'fl4-c'),
                    'rightwing': self.get_player_in_line_pos(soup, 'fl4-rw')
                },
            ],
            'defense': [
                {
                    'left': self.get_player_in_line_pos(soup, 'dl1-ld'),
                    'right': self.get_player_in_line_pos(soup, 'dl1-rd')
                },
                {
                    'left': self.get_player_in_line_pos(soup, 'dl2-ld'),
                    'right': self.get_player_in_line_pos(soup, 'dl2-rd')
                },
                {
                    'left': self.get_player_in_line_pos(soup, 'dl3-ld'),
                    'right': self.get_player_in_line_pos(soup, 'dl3-rd')
                }
            ],
            'goalies': [
                self.get_player_in_line_pos(soup, 'gl-1'),
                self.get_player_in_line_pos(soup, 'gl-2'),
            ]

        }
        return self.construct_line_str(lines)

    def construct_line_str(self, lines):
        line_str = '---FORWARDS---'
        for line in lines.get('forwards'):
            lw = line.get('leftwing', None)
            rw = line.get('rightwing', None)
            center = line.get('center', None)
            lw = '' if lw is None else lw
            rw = '' if rw is None else rw
            center = '' if center is None else center
            if all(v is None for v in line.values()) is False:
                line_str = '{0}\r\n{1} - {2} - {3}'.format(line_str, lw,
                                                           center, rw)
        line_str = '{0}\r\n---DEFENSE---'.format(line_str)
        for line in lines.get('defense'):
            ld = line.get('left', None)
            rd = line.get('right', None)
            ld = '' if ld is None else ld
            rd = '' if rd is None else rd
            if all(v is None for v in line.values()) is False:
                line_str = '{0}\r\n{1} - {2}'.format(line_str, ld, rd)
        line_str = '{0}\r\n---GOALIES---'.format(line_str)
        for goalie in lines.get('goalies'):
            if goalie is not None:
                line_str = '{0}\r\n{1}'.format(line_str, goalie)
        return line_str

    def get_player_in_line_pos(self, soup, pos):
        pos_item = soup.find('div', {'data-position': pos})
        if pos_item is None:
            return None
        player_item = pos_item.find('span', {'class': 'playerName'})
        player_num = player_item.span
        player_name = player_num.previous_sibling
        return player_name.strip()

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
                self.session.get('{0}{1}'.format(DEFAULT_URL, CHECKIN_URL),
                                 params=data)
            except Exception:
                raise CheckinException(
                    "ERROR::Could not check in {0}".format(name))


def main():
    assert len(sys.argv) > 2
    ba = BenchApp(sys.argv[1], sys.argv[2])
    logging.debug(ba.get_next_game_attendees())
    logging.debug(ba.get_next_game_attendance())
    logging.debug(ba.get_next_game_lines())


if __name__ == '__main__':
    main()
