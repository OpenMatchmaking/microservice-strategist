from app.algorithms import BaseAlgorithm
from app.utils import get_all_subclasses


class GameMode(object):

    def __init__(self, name, teams, team_size, algorithm):
        super(GameMode, self).__init__()
        self.name = name
        self.teams = teams
        self.team_size = team_size
        self.algorithm = self.init_algorithm(algorithm)

    def init_algorithm(self, name):
        available_algorithms = {
            cls.__name__.lower(): cls
            for cls in get_all_subclasses(BaseAlgorithm)
        }

        try:
            name = name.lower().strip()
            algorithm = available_algorithms[name]
        except KeyError as exc:
            found_algorithms = list(available_algorithms.keys())
            message = "The matchmaking algorithm with the name=\"{}\" wasn't found. " \
                      "Available algorithms: {}".format(name, found_algorithms)
            raise ValueError(message) from exc

        return algorithm(self.team_size)

    def create_empty_teams(self, amount):
        return {
            "team {}".format(team_number): []
            for team_number in range(1, amount + 1)
        }

    def seed_player(self, player, grouped_players, **kwargs):
        if not grouped_players:
            grouped_players = self.create_empty_teams(self.teams)
        return self.algorithm.seed_player(player, grouped_players, **kwargs)
