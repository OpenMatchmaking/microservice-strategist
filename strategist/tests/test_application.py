import os

from unittest import TestCase

from app.application import App


class ApplicationTestCase(TestCase):

    def test_application_without_config_and_game_modes(self):
        old_config_path = os.environ.get(App.env_config_var)
        os.environ[App.env_config_var] = ''
        app = App()

        self.assertEqual(app.config, {})
        self.assertEqual(app.game_modes, {})

        os.environ[App.env_config_var] = old_config_path

    def test_application_has_init_successfully(self):
        app = App()

        self.assertNotEqual(app.config, {})
        self.assertNotEqual(app.game_modes, {})
