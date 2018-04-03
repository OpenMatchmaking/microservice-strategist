import pytest

from app.workers.match_check.worker import MatchCheckWorker
from tests.workers.amqp_client import AmqpTestClient


REQUEST_QUEUE = MatchCheckWorker.QUEUE_NAME
REQUEST_EXCHANGE = MatchCheckWorker.REQUEST_EXCHANGE_NAME
RESPONSE_EXCHANGE = MatchCheckWorker.RESPONSE_EXCHANGE_NAME


@pytest.mark.asyncio
async def test_worker_returns_a_validation_error_for_missing_fields(test_app):
    client = AmqpTestClient(
        test_app,
        routing_key=REQUEST_QUEUE,
        request_exchange=REQUEST_EXCHANGE,
        response_queue='',
        response_exchange=RESPONSE_EXCHANGE
    )
    response = await client.send(payload={})

    assert 'error' in response.keys()

    assert 'type' in response['error'].keys()
    assert response['error']['type'] == "ValidationError"

    assert 'details' in response['error'].keys()
    assert len(response['error']['details']) == 3

    for field in ['game-mode', 'new-player', 'grouped-players']:
        assert field in response['error']['details']
        assert len(response['error']['details'][field]) == 1
        assert response['error']['details'][field][0] == 'Missing data for required field.'


@pytest.mark.asyncio
async def test_worker_returns_a_validation_error_for_invalid_game_mode(test_app):
    client = AmqpTestClient(
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

    assert 'error' in response.keys()

    assert 'type' in response['error'].keys()
    assert response['error']['type'] == "ValidationError"

    assert 'details' in response['error'].keys()
    assert len(response['error']['details']) == 1

    assert 'game-mode' in response['error']['details']
    assert len(response['error']['details']['game-mode']) == 1
    assert response['error']['details']['game-mode'][0] == 'The specified game mode ' \
                                                           'is not available.'


@pytest.mark.asyncio
async def test_worker_returns_an_updated_grouped_players(test_app):
    client = AmqpTestClient(
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

    assert 'content' in response.keys()
    assert 'event-name' in response.keys()

    assert 'added' in response['content'].keys()
    assert response['content']['added'] is True

    assert 'grouped-players' in response['content'].keys()
    assert len(response['content']['grouped-players']['team 1']) == 1
    assert payload['new-player'] not in response['content']['grouped-players']['team 1']
    assert len(response['content']['grouped-players']['team 2']) == 1
    assert payload['new-player'] in response['content']['grouped-players']['team 2']

@pytest.mark.asyncio
async def test_worker_returns_the_grouped_players_without_any_changes(test_app):
    client = AmqpTestClient(
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

    assert 'content' in response.keys()
    assert 'event-name' in response.keys()

    assert 'added' in response['content'].keys()
    assert response['content']['added'] is False

    assert 'grouped-players' in response['content'].keys()
    assert response['content']['grouped-players'] == payload['grouped-players']
