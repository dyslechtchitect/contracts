import pytest
import run_server


@pytest.fixture()
def app():
    app = run_server.app
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_request_example(client):
    response = client.post("/contract")
    assert b"<h2>Hello, World!</h2>" in response.data