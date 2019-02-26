class Team(object):

    def __init__(self, name, points=0, games_played=0, wins=0, losses=0,
                 ties=0, goals_for=0, goals_against=0, division='0-0-0'):
        self.name = name
        self.points = points
        self.games_played = games_played
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.division = division

    def __repr__(self):
        return '{0}:\t{1} pts\t({2})'.format(self.name,
                                             self.points,
                                             self.division)

    @property
    def full_description(self):
        full = ("{}\t| {} Points \t| {} Games Played \t| {} Wins \t|"
                " {} Losses \t| {} Ties \t| {} Goals For \t|"
                " {} Goals Against \t| {} |")
        return full.format(self.name, self.points, self.games_played,
                           self.wins, self.losses, self.ties, self.goals_for,
                           self.goals_against, self.division)

    def get_average(self, stat):
        return float(stat) / float(self.games_played)

    @property
    def goals_average(self):
        return self.get_average(self.goals_for)

    @property
    def points_average(self):
        return self.get_average(self.points)

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

    def get_stat(self, stat_name):
        stat_dict = {
            'gp': self.games_played,
            'games_played': self.games_played,
            'games': self.games_played,
            'name': self.name,
            'goals': self.goals_for,
            'goal': self.goals_for,
            'g': self.goals_for,
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
            'division_record': self.division,
            'division': self.division,
            'record': self.division,
            'd': self.division,
            'goals_average': self.goals_average,
            'g_avg': self.goals_average,
            'gavg': self.goals_average,
            'gav': self.goals_average,
            'points_average': self.points_average,
            'p_avg': self.points_average,
            'pavg': self.points_average,
            'pa': self.points_average,
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
        return stat_dict.get(stat_name)
