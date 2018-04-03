import json

from aioamqp import AmqpClosedConnection

from app.amqp.base import AmqpWorker
from app.workers.schemas import RequestDataSchema
from marshmallow import ValidationError


class MatchCheckWorker(AmqpWorker):
    PREFETCH_COUNT = 10
    QUEUE_NAME = "strategist.match.check"
    REQUEST_EXCHANGE_NAME = "open-matchmaking.strategist.check.fanout"
    RESPONSE_EXCHANGE_NAME = "open-matchmaking.responses.direct"
    CONTENT_TYPE = 'application/json'

    def validate_data(self, raw_data):
        try:
            data = json.loads(raw_data.strip())
        except json.decoder.JSONDecodeError:
            data = {}

        deserializer = RequestDataSchema()
        result = deserializer.load(data)

        if result["game-mode"] not in self.app.game_modes.keys():
            raise ValidationError(
                "The specified game mode is not available.",
                field_names=["game-mode", ]
            )

        return result

    def seed_player(self, game_mode, player, teams):
        added, teams = game_mode.seed_player(player, teams)
        return {
            "added": added,
            "grouped-players": teams
        }

    async def process_request(self, channel, body, envelope, properties):
        try:
            data = self.validate_data(body)
            game_mode = self.app.game_modes[data["game-mode"]]
            player = data["new-player"]
            grouped_players = data["grouped-players"]
            response = self.seed_player(game_mode, player, grouped_players)
        except ValidationError as exc:
            response = {"errors": [{"Validation error": exc.normalized_messages()}]}

        if properties.reply_to:
            await channel.publish(
                json.dumps(response),
                exchange_name=self.RESPONSE_EXCHANGE_NAME,
                routing_key=properties.reply_to,
                properties={
                    'content_type': self.CONTENT_TYPE,
                    'delivery_mode': 2,
                    'correlation_id': properties.correlation_id
                },
                mandatory=True
            )

        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def consume_callback(self, channel, body, envelope, properties):
        self.app.loop.create_task(self.process_request(channel, body, envelope, properties))

    async def run(self, *args, **kwargs):
        try:
            _transport, protocol = await self.connect()
            print("A new AMQP connection has been established...")
        except AmqpClosedConnection as exc:
            print(exc)
            return

        concurrency = self.app.config.get('APP_WORKERS', 1)
        channel = await protocol.channel()

        await channel.exchange_declare(
            exchange_name=self.REQUEST_EXCHANGE_NAME,
            type_name='fanout',
            durable=True,
            passive=False
        )
        await channel.queue_declare(
            queue_name=self.QUEUE_NAME,
            durable=True,
            passive=False,
            auto_delete=False
        )
        await channel.queue_bind(
            queue_name=self.QUEUE_NAME,
            exchange_name=self.REQUEST_EXCHANGE_NAME,
            routing_key=self.QUEUE_NAME
        )
        await channel.basic_qos(
            prefetch_count=self.PREFETCH_COUNT * concurrency,
            prefetch_size=0,
            connection_global=False
        )
        await channel.basic_consume(self.consume_callback, queue_name=self.QUEUE_NAME)
