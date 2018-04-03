from marshmallow import Schema, fields, validates, ValidationError


class RequestDataSchema(Schema):
    game_mode = fields.String(
        attribute="game-mode",
        data_key="game-mode",
        required=True,
        allow_none=False,
    )
    new_player = fields.Dict(
        attribute="new-player",
        data_key="new-player",
        required=True,
        allow_none=False,
    )
    grouped_players = fields.Dict(
        attribute="grouped-players",
        data_key="grouped-players",
        required=True,
        allow_none=False,
    )
