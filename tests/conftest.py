import pytest
from flask_login import FlaskLoginClient

from app import app, config
from app.models import User

@pytest.fixture(scope='module')
def app_tst():
    app.test_client_class = FlaskLoginClient
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def client_all_access(app_tst):
    user = User.query.get(1)
    with app_tst.test_client(user=user) as client:
        with client.session_transaction() as session:
            session['meta_data'] = ""
    yield client
    
@pytest.fixture(scope='module')
def client_partial_access(app_tst):
    user = User.query.get(1)
    with app_tst.test_client(user=user) as client:
        with client.session_transaction() as session:
            session['meta_data'] = ""
    yield client

@pytest.fixture(scope='module')
def client_unauth(app_tst):
    client = app_tst.test_client()
    yield client
    
@pytest.fixture
def random_string_const():
    return "ABCHSK"