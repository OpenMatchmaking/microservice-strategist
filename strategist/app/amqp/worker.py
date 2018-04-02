from aioamqp import AmqpClosedConnection

from app.amqp.base import AmqpWorker


class MatchCheckWorker(AmqpWorker):
    PREFETCH_COUNT = 10
    QUEUE_NAME = "strategist.match.check"
    REQUEST_EXCHANGE_NAME = "open-matchmaking.strategist.check.fanout"
    RESPONSE_EXCHANGE_NAME = "open-matchmaking.responses.direct"
    CONTENT_TYPE = 'application/json'

    async def process_request(self, channel, body, envelope, properties):
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
