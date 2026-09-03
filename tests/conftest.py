import pytest 
from donor_outreach.app import create_app
from donor_outreach.config import get_settings
from donor_outreach.extensions import db

@pytest.fixture
def app():
    settings = get_settings()
    flask_app = create_app()
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = settings.test_database_url
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    return app.test_client()



