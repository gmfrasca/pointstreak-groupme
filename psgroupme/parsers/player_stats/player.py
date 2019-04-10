DEFAULT_THRESHOLD = 3


class Player(object):

    def __init__(self, name, jersey_number=0, games_played=0, goals=0,
                 assists=0, penalties=0, penalties_in_minutes=0,
                 wins=0, losses=0, ties=0, goals_against=0):
        self.name = name
        self.jersey_number = jersey_number
        self.games_played = games_played
        self.goals = goals
        self.assists = assists
        self.penalties = penalties
        self.penalties_in_minutes = penalties_in_minutes
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.goals_against = goals_against

    def __repr__(self):
        return '{0}\t{1}'.format(self.jersey_number, self.name)

    # Player Stats
    @property
    def points(self):
        return int(self.goals) + int(self.assists)

    @property
    def goals_average(self):
        return self.get_average(self.goals)

    @property
    def assists_average(self):
        return self.get_average(self.assists)

    @property
    def points_average(self):
        return self.get_average(self.points)

    @property
    def penalties_average(self):
        return self.get_average(self.penalties)

    # Goalie Stats
    @property
    def wins_average(self):
        return self.get_average(self.wins)

    @property
    def losses_average(self):
        return self.get_average(self.losses)

    @property
    def ties_average(self):
        return self.get_average(self.ties)

    @property
    def goals_against_average(self):
        return self.get_average(self.goals_against)

    # Playoff Elligibility
    def is_playoff_eligible(self, sched_length, round_down=True,
                            grace_games=0, games_needed=None, *args, **kwargs):
        needed = self.games_needed_for_playoff_elligible(sched_length,
                                                         round_down,
                                                         grace_games,
                                                         games_needed)
        return needed <= 0

    def games_needed_for_playoff_elligible(self, sched_length, round_down=True,
                                           grace_games=0, games_needed=None):
        if games_needed is not None:
            return games_needed - int(self.games_played)
        needed = sched_length / 2
        if round_down:
            needed -= needed % 2
        needed -= grace_games
        return needed - int(self.games_played)

    def can_be_elligible(self, sched_length, games_remaining,
                         round_down=True, grace_games=0, games_needed=None,
                         *args, **kwargs):
        return self.get_missable_games(sched_length, games_remaining,
                                       round_down, grace_games,
                                       games_needed) >= 0

    def in_danger_of_inelligibility(self, sched_length, games_remaining,
                                    round_down=True, grace_games=0,
                                    warning_threshold=DEFAULT_THRESHOLD,
                                    games_needed=None, *args, **kwargs):
        possible_missed = self.get_missable_games(sched_length,
                                                  games_remaining,
                                                  round_down, grace_games,
                                                  games_needed)
        return (possible_missed >= 0 and possible_missed <= warning_threshold)

    def get_missable_games(self, sched_length, games_remaining,
                           round_down=True, grace_games=0, games_needed=None,
                           *args, **kwargs):
        needed = self.games_needed_for_playoff_elligible(sched_length,
                                                         round_down,
                                                         grace_games,
                                                         games_needed)
        return games_remaining - needed

    def get_average(self, stat):
        return float(stat) / float(self.games_played)

    def get_stat(self, stat_name):
        stat_dict = {
            'gp': self.games_played,
            'games_played': self.games_played,
            'games': self.games_played,
            'name': self.name,
            'jersey_number': self.jersey_number,
            'number': self.jersey_number,
            'goals': self.goals,
            'goal': self.goals,
            'g': self.goals,
            'assists': self.assists,
            'assist': self.assists,
            'a': self.assists,
            'penalties': self.penalties,
            'penalty': self.penalties,
            'pens': self.penalties,
            'pen': self.penalties,
            'penalties_in_minutes': self.penalties_in_minutes,
            'penalty_minutes': self.penalties_in_minutes,
            'pims': self.penalties_in_minutes,
            'pim': self.penalties_in_minutes,
            'wins': self.wins,
            'win': self.wins,
            'w': self.wins,
            'losses': self.losses,
            'loss': self.losses,
            'l': self.losses,
            'ties': self.ties,
            'tie': self.ties,
            't': self.ties,
            'goals_against': self.goals_against,
            'ga': self.goals_against,
            'points': self.points,
            'point': self.points,
            'pts': self.points,
            'p': self.points,
            'goals_average': self.goals_average,
            'g_avg': self.goals_average,
            'gavg': self.goals_average,
            'gav': self.goals_average,
            'assists_average': self.assists_average,
            'a_avg': self.assists_average,
            'aavg': self.assists_average,
            'aa': self.assists_average,
            'points_average': self.points_average,
            'p_avg': self.points_average,
            'pavg': self.points_average,
            'pa': self.points_average,
            'penalties_average': self.penalties_average,
            'pen_avg': self.penalties_average,
            'penavg': self.penalties_average,
            'pena': self.penalties_average,
            'wins_average': self.wins_average,
            'w_avg': self.wins_average,
            'wavg': self.wins_average,
            'wa': self.wins_average,
            'losses_average': self.losses_average,
            'l_avg': self.losses_average,
            'lavg': self.losses_average,
            'la': self.losses_average,
            'ties_average': self.ties_average,
            't_avg': self.ties_average,
            'tavg': self.ties_average,
            'ta': self.ties_average,
            'goals_against_average': self.goals_against_average,
            'ga_avg': self.goals_against_average,
            'gaa': self.goals_against_average,
            'gaavg': self.goals_against_average
        }
        return stat_dict.get(stat_name, None)
