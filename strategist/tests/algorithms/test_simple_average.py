from unittest import TestCase
from uuid import uuid4

from app.algorithms.simple_average import SimpleAverage


class SimpleAlgorithmTestCase(TestCase):

    def generate_player_data(self, game_mode, rating):
        return {
            "id": str(uuid4()),
            "response-queue": "{}-response-queue".format(str(uuid4())),
            "event-name": game_mode,
            "detail": {
                "rating": rating,
                "content": {}
            }
        }

    def test_seed_player_in_1v1(self):
        new_player = self.generate_player_data("1v1", 2479)
        teams = {
            "team 1": [self.generate_player_data("1v1", 2500)],
            "team 2": []
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, teams)

        self.assertTrue(added)
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 1)
        self.assertIn(new_player, updated_teams["team 2"])

    def test_seed_player_in_1v1_with_empty_groups(self):
        new_player = self.generate_player_data("1v1", 2500)
        teams = {
            "team 1": [],
            "team 2": []
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, teams)

        self.assertTrue(added)
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 0)
        self.assertIn(new_player, updated_teams["team 1"])

    def test_seed_player_in_1v1_doesnt_do_changes(self):
        new_player = self.generate_player_data("1v1", 2500)
        teams = {
            "team 1": [self.generate_player_data("1v1", 2900)],
            "team 2": []
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, teams)

        self.assertFalse(added)
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 0)
        self.assertNotIn(new_player, updated_teams["team 1"])

    def test_seed_player_in_team_deathmatch(self):
        new_player = self.generate_player_data("team-deathmatch", 2491)
        teams = {
            "team 1": [
                self.generate_player_data("team-deathmatch", 2500),
                self.generate_player_data("team-deathmatch", 2498),
            ],
            "team 2": [
                self.generate_player_data("team-deathmatch", 2512),
            ]
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, teams)

        self.assertTrue(added)
        self.assertEqual(len(updated_teams["team 1"]), 2)
        self.assertEqual(len(updated_teams["team 2"]), 2)
        self.assertIn(new_player, updated_teams["team 2"])

    def test_seed_player_in_team_deathmatch_with_empty_groups(self):
        new_player = self.generate_player_data("team-deathmatch", 2500)
        rating_groups = {
            "team 1": [],
            "team 2": []
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, rating_groups)

        self.assertTrue(added)
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 0)
        self.assertIn(new_player, updated_teams["team 1"])

    def test_seed_player_in_team_deathmatch_doesnt_do_changes(self):
        new_player = self.generate_player_data("team-deathmatch", 2000)
        teams = {
            "team 1": [
                self.generate_player_data("team-deathmatch", 2500),
            ],
            "team 2": [
                self.generate_player_data("team-deathmatch", 2512),
            ]
        }

        algorithm = SimpleAverage()
        added, updated_teams = algorithm.seed_player(new_player, teams)

        self.assertFalse(added)
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 1)
        self.assertNotIn(new_player, updated_teams["team 1"])
        self.assertNotIn(new_player, updated_teams["team 2"])
