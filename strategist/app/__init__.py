from sage_utils.amqp.extension import AmqpExtension

from app.application import App
from app.workers.match_check.worker import MatchCheckWorker


app = App()
app.amqp = AmqpExtension(app)
app.amqp.register_worker(MatchCheckWorker(app))
