import os


SERVICE_NAME = 'strategist'
SERVICE_VERSION = '0.1.0'


def to_bool(value):
    return str(value).strip().lower() in ['1', 'true', 'yes']


def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


APP_WORKERS = int((os.environ.get('APP_WORKERS', 1)))
APP_GAME_MODES_CONFIGURATION = {
    'duel': {
        'teams': 2,
        'team_size': 1,
        'algorithm': 'SimpleAverage'
    },
    'team-deathmatch': {
        'teams': 2,
        'team_size': 5,
        'algorithm': 'SimpleAverage'
    }
}

# AMQP settings
AMQP_USERNAME = os.environ.get("AMQP_USERNAME", "user")
AMQP_PASSWORD = os.environ.get("AMQP_PASSWORD", "password")
AMQP_HOST = os.environ.get("AMQP_HOST", "rabbitmq")
AMQP_PORT = to_int(os.environ.get("AMQP_PORT", 5672))
AMQP_VIRTUAL_HOST = os.environ.get("AMQP_VIRTUAL_HOST", "vhost")
AMQP_USING_SSL = to_bool(os.environ.get("AMQP_USING_SSL", False))
