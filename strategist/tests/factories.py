from uuid import uuid4


def generate_player_data(event_name, rating):
    return {
        "id": str(uuid4()),
        "response-queue": "{}-response-queue".format(str(uuid4())),
        "event-name": event_name,
        "detail": {
            "rating": rating,
            "content": {}
        }
    }
