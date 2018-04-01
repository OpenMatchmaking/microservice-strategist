

class BaseAlgorithm(object):

    def __init__(self, team_size, *args, **kwargs):
        super(BaseAlgorithm, self).__init__()
        self.team_size = team_size

    def seed_player(self, player, teams, **kwargs):
        raise NotImplementedError("The `seed_player(player, teams, **kwargs)` "
                                  "method must be implemented.")
