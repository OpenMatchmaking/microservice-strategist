import pytest

from sage_utils.amqp.clients import RpcAmqpClient
from sage_utils.constants import VALIDATION_ERROR
from sage_utils.wrappers import Response
from app.workers.match_check.worker import MatchCheckWorker


REQUEST_QUEUE = MatchCheckWorker.QUEUE_NAME
REQUEST_EXCHANGE = MatchCheckWorker.REQUEST_EXCHANGE_NAME
RESPONSE_EXCHANGE = MatchCheckWorker.RESPONSE_EXCHANGE_NAME


@pytest.mark.asyncio
async def test_worker_returns_a_validation_error_for_missing_fields(test_app):
    client = RpcAmqpClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    response = await client.send(payload={})

    assert Response.ERROR_FIELD_NAME in response.keys()
    error = response[Response.ERROR_FIELD_NAME]

    assert Response.ERROR_TYPE_FIELD_NAME in error.keys()
    assert error[Response.ERROR_TYPE_FIELD_NAME] == VALIDATION_ERROR

    assert Response.ERROR_DETAILS_FIELD_NAME in error.keys()
    assert len(error[Response.ERROR_DETAILS_FIELD_NAME]) == 3

    for field in ['game-mode', 'new-player', 'grouped-players']:
        assert field in error[Response.ERROR_DETAILS_FIELD_NAME]
        assert len(error[Response.ERROR_DETAILS_FIELD_NAME][field]) == 1
        assert error[Response.ERROR_DETAILS_FIELD_NAME][field][0] == 'Missing data for ' \
                                                                     'required field.'


@pytest.mark.asyncio
async def test_worker_returns_a_validation_error_for_invalid_game_mode(test_app):
    client = RpcAmqpClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    payload = {
        "game-mode": "UNKNOWN_MODE",
        "new-player": {
            "id": "0146563d-0f45-4062-90a7-b13a583defad",
            "response-queue": "player-2-queue",
            "event-name": "find-game",
            "detail": {
                "rating": 2680,
                "content": {
                    "id": "0146563d-0f45-4062-90a7-b13a583defad",
                    "games": 531,
                    "wins": 279
                }
            }
        },
        "grouped-players": {
            "team 1": [
                {
                    "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                    "response-queue": "player-1-queue",
                    "event-name": "find-game",
                    "detail": {
                        "rating": 2702,
                        "content": {
                            "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                            "games": 161,
                            "wins": 91
                        }
                    }
                }
            ],
            "team 2": []
        }
    }
    response = await client.send(payload=payload)

    assert Response.ERROR_FIELD_NAME in response.keys()
    error = response[Response.ERROR_FIELD_NAME]

    assert Response.ERROR_TYPE_FIELD_NAME in error.keys()
    assert error[Response.ERROR_TYPE_FIELD_NAME] == VALIDATION_ERROR

    assert Response.ERROR_DETAILS_FIELD_NAME in error.keys()
    assert len(error[Response.ERROR_DETAILS_FIELD_NAME]) == 1

    assert 'game-mode' in error['details']
    assert len(error[Response.ERROR_DETAILS_FIELD_NAME]['game-mode']) == 1
    assert error[Response.ERROR_DETAILS_FIELD_NAME]['game-mode'][0] == 'The specified game mode ' \
                                                                       'is not available.'


@pytest.mark.asyncio
async def test_worker_returns_an_updated_grouped_players(test_app):
    client = RpcAmqpClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    payload = {
        "game-mode": "duel",
        "new-player": {
            "id": "0146563d-0f45-4062-90a7-b13a583defad",
            "response-queue": "player-2-queue",
            "event-name": "find-game",
            "detail": {
                "rating": 2680,
                "content": {
                    "id": "0146563d-0f45-4062-90a7-b13a583defad",
                    "games": 531,
                    "wins": 279
                }
            }
        },
        "grouped-players": {
            "team 1": [
                {
                    "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                    "response-queue": "player-1-queue",
                    "event-name": "find-game",
                    "detail": {
                        "rating": 2702,
                        "content": {
                            "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                            "games": 161,
                            "wins": 91
                        }
                    }
                }
            ],
            "team 2": []
        }
    }
    response = await client.send(payload=payload)

    assert Response.CONTENT_FIELD_NAME in response.keys()
    assert Response.EVENT_FIELD_NAME in response.keys()
    content = response[Response.CONTENT_FIELD_NAME]

    assert 'added' in content.keys()
    assert content['added'] is True

    assert 'is_filled' in response['content'].keys()
    assert content['is_filled'] is True

    assert 'grouped-players' in content.keys()
    assert len(content['grouped-players']['team 1']) == 1
    assert payload['new-player'] not in content['grouped-players']['team 1']
    assert len(content['grouped-players']['team 2']) == 1
    assert payload['new-player'] in content['grouped-players']['team 2']


@pytest.mark.asyncio
async def test_worker_returns_the_grouped_players_without_any_changes(test_app):
    client = RpcAmqpClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    payload = {
        "game-mode": "duel",
        "new-player": {
            "id": "0146563d-0f45-4062-90a7-b13a583defad",
            "response-queue": "player-2-queue",
            "event-name": "find-game",
            "detail": {
                "rating": 3500,
                "content": {
                    "id": "0146563d-0f45-4062-90a7-b13a583defad",
                    "games": 531,
                    "wins": 279
                }
            }
        },
        "grouped-players": {
            "team 1": [
                {
                    "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                    "response-queue": "player-1-queue",
                    "event-name": "find-game",
                    "detail": {
                        "rating": 2702,
                        "content": {
                            "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                            "games": 161,
                            "wins": 91
                        }
                    }
                }
            ],
            "team 2": []
        }
    }
    response = await client.send(payload=payload)

    assert Response.CONTENT_FIELD_NAME in response.keys()
    assert Response.EVENT_FIELD_NAME in response.keys()
    content = response[Response.CONTENT_FIELD_NAME]

    assert 'added' in content.keys()
    assert content['added'] is False

    assert 'is_filled' in content.keys()
    assert content['is_filled'] is False

    assert 'grouped-players' in content.keys()
    assert content['grouped-players'] == payload['grouped-players']


@pytest.mark.asyncio
async def test_worker_returns_the_grouped_players_without_any_changes_when_try_seeding(test_app):
    client = RpcAmqpClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    payload = {
        "game-mode": "duel",
        "new-player": {
            "id": "0146563d-0f45-4062-90a7-b13a583defad",
            "response-queue": "player-3-queue",
            "event-name": "find-game",
            "detail": {
                "rating": 2680,
                "content": {
                    "id": "0146563d-0f45-4062-90a7-b13a583defad",
                    "games": 531,
                    "wins": 279
                }
            }
        },
        "grouped-players": {
            "team 1": [
                {
                    "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                    "response-queue": "player-1-queue",
                    "event-name": "find-game",
                    "detail": {
                        "rating": 2702,
                        "content": {
                            "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                            "games": 161,
                            "wins": 91
                        }
                    }
                }
            ],
            "team 2": [
                {
                    "id": "56acbeb4-687d-4c8b-a881-0b9abdda64e4",
                    "response-queue": "player-2-queue",
                    "event-name": "find-game",
                    "detail": {
                        "rating": 2695,
                        "content": {
                            "id": "343e8c2d-6fda-40df-b859-90c5bafecb61",
                            "games": 215,
                            "wins": 126
                        }
                    }
                }
            ]
        }
    }
    response = await client.send(payload=payload)

    assert Response.CONTENT_FIELD_NAME in response.keys()
    assert Response.EVENT_FIELD_NAME in response.keys()
    content = response[Response.CONTENT_FIELD_NAME]

    assert 'added' in content.keys()
    assert content['added'] is False

    assert 'is_filled' in content.keys()
    assert content['is_filled'] is True

    assert 'grouped-players' in content.keys()
    assert len(content['grouped-players']['team 1']) == 1
    assert payload['new-player'] not in content['grouped-players']['team 1']
    assert len(content['grouped-players']['team 2']) == 1
    assert payload['new-player'] not in content['grouped-players']['team 2']
