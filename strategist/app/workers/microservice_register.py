from app.amqp.amqp_client import RpcAmqpClient
from app.amqp.base import AmqpWorker


class MicroserviceRegisterWorker(AmqpWorker):
    REQUEST_QUEUE_NAME = "auth.microservices.register"
    REQUEST_EXCHANGE_NAME = "open-matchmaking.direct"
    RESPONSE_EXCHANGE_NAME = "open-matchmaking.responses.direct"
    CONTENT_TYPE = 'application/json'

    def get_microservice_data(self, app):
        return {
            'name': self.app.config['SERVICE_NAME'],
            'version': self.app.config['SERVICE_VERSION'],
            'permissions': []
        }

    async def run(self, *args, **kwargs):
        client = RpcAmqpClient(
            self.app,
            routing_key=self.REQUEST_QUEUE_NAME,
            request_exchange=self.REQUEST_EXCHANGE_NAME,
            response_queue='',
            response_exchange=self.RESPONSE_EXCHANGE_NAME
        )
        response = await client.send(self.get_microservice_data(self.app))

        assert 'error' not in response.keys(), response['error']
        assert 'content' in response.keys()
        assert response['content'] == 'OK'
