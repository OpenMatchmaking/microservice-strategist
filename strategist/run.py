from app.application import App
from app.amqp.extension import AmqpExtension
from app.amqp.worker import MatchCheckWorker


app = App()
app.amqp = AmqpExtension(app)
app.amqp.register_worker(MatchCheckWorker(app))

app.run()
