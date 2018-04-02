import asyncio
import os
from types import ModuleType
from pathlib import Path

from app.game_mode import GameMode


class App(object):
    env_config_var = 'APP_CONFIG_PATH'
    conf_game_modes_var = 'APP_GAME_MODES_CONFIGURATION'

    def __init__(self, *args, **kwargs):
        super(App, self).__init__()
        config_path = os.environ.get(self.env_config_var, None)
        self.config = self.load_config(config_path)
        self.game_modes = self.load_game_modes(self.config)
        self.extensions = {}

    def load_config(self, config_path):
        if not Path(config_path).is_file():
            return {}

        module = ModuleType(name='Config')
        module.__file__ = config_path
        with open(config_path) as config_file:
            code_object = compile(config_file.read(), config_path, 'exec')
            exec(code_object, module.__dict__)

        return {
            key: getattr(module, key)
            for key in dir(module)
            if key.isupper()
        }

    def load_game_modes(self, config):
        game_mode_configurations = config.get(self.conf_game_modes_var, {})
        return {
            game_mode_name: GameMode(game_mode_name, **options)
            for (game_mode_name, options) in game_mode_configurations.items()
        }

    def await_tasks(self, tasks, loop):
        for task in tasks:
            loop.run_until_complete(task)

    def run(self, *arg, **kwargs):
        self.loop = asyncio.get_event_loop()

        try:
            tasks = []
            for worker in self.extensions.values():
                init_task = asyncio.ensure_future(worker.init(self.loop))
                tasks.append(init_task)

            self.await_tasks(tasks, self.loop)
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            tasks = []
            for worker in self.extensions.values():
                deinit_task = asyncio.ensure_future(worker.deinit(self.loop))
                tasks.append(deinit_task)

            self.await_tasks(tasks, self.loop)
            self.loop.close()
