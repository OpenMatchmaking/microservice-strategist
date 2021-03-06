import pytest

from app.application import App
from app.workers.match_check.worker import MatchCheckWorker

from sage_utils.amqp import AmqpExtension


@pytest.fixture(scope="function")
def test_app(event_loop):
    app = App()
    app.amqp = AmqpExtension(app)
    app.amqp.register_worker(MatchCheckWorker(app))

    app.loop = event_loop
    app.init_workers(event_loop)
    yield app
    app.deinit_workers(event_loop)
    app.loop = None
