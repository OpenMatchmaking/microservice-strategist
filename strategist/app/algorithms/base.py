

class BaseAlgorithm(object):

    def seed_player(self, player, teams, **kwargs):
        raise NotImplementedError("The `seed_player(player, teams, **kwargs)` "
                                  "method must be implemented.")
