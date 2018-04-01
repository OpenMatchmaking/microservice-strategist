import os


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
