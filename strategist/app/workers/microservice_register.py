from sage_utils.amqp.workers import BaseRegisterWorker


class MicroserviceRegisterWorker(BaseRegisterWorker):

    def get_microservice_data(self, app):
        return {
            'name': self.app.config['SERVICE_NAME'],
            'version': self.app.config['SERVICE_VERSION'],
            'permissions': []
        }
