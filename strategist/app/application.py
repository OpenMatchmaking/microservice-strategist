import os
from types import ModuleType


class App(object):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__()
        config_path = os.environ.get('APP_CONFIG_PATH', None)
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        if config_path is None:
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

    def run(self, *arg, **kwargs):
        # TODO: Run AMQP workers here
        pass
