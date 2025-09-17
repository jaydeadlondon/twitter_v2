import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Tweet, Follow, Like, Media


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to use as database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            api_key='test-api-key-123'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_users(app):
    """Create multiple sample users for testing."""
    with app.app_context():
        users = [
            User(username='alice', email='alice@test.com', api_key='alice-key'),
            User(username='bob', email='bob@test.com', api_key='bob-key'),
            User(username='charlie', email='charlie@test.com', api_key='charlie-key')
        ]
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        return users


@pytest.fixture
def auth_headers():
    """Return authorization headers for testing."""
    return {'api-key': 'test-api-key-123'}
