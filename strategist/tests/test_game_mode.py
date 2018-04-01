from unittest import TestCase

from app.game_mode import GameMode
from tests.factories import generate_player_data


class GameModeTestCase(TestCase):

    def test_game_mode_init_returns_a_value_error_for_invalid_algorithm_name(self):
        with self.assertRaises(ValueError):
            GameMode('duel', 2, 1, 'NOT_EXISTING_ALGORITHM')

    def test_game_mode_seeds_a_player_and_created_new_teams(self):
        game_mode = GameMode('duel', 2, 1, 'SimpleAverage')
        new_player = generate_player_data('find-opponent', 2500)

        added, updated_teams = game_mode.seed_player(new_player, {})

        self.assertTrue(added)
        self.assertEqual({"team 1", "team 2"}, set(updated_teams.keys()))
        self.assertEqual(len(updated_teams["team 1"]), 1)
        self.assertEqual(len(updated_teams["team 2"]), 0)
        self.assertIn(new_player, updated_teams["team 1"])

    def test_game_mode_seeds_a_player_into_existing_teams(self):
        game_mode = GameMode('duel', 2, 1, 'SimpleAverage')
        new_player = generate_player_data("1v1", 2479)
        teams = {
            "team 1": [generate_player_data("1v1", 2500)],
            "team 2": []
        }

        added, updated_groups = game_mode.seed_player(new_player, teams)

        self.assertTrue(added)
        self.assertEqual(len(updated_groups["team 1"]), 1)
        self.assertEqual(len(updated_groups["team 2"]), 1)
        self.assertIn(new_player, updated_groups["team 2"])
