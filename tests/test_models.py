import pytest
from app import db
from app.models import User, Tweet, Follow, Like, Media


def test_user_model(app):
    """Test User model creation and methods."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            api_key='test-key-123'
        )
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.api_key == 'test-key-123'
        assert user.created_at is not None


def test_user_to_dict(app):
    """Test User to_dict method."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            api_key='test-key-123'
        )
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        assert user_dict['id'] == user.id
        assert user_dict['name'] == 'testuser'
        assert 'followers' in user_dict
        assert 'following' in user_dict


def test_tweet_model(app, sample_user):
    """Test Tweet model creation and methods."""
    with app.app_context():
        tweet = Tweet(
            user_id=sample_user.id,
            content='This is a test tweet'
        )
        db.session.add(tweet)
        db.session.commit()
        
        assert tweet.id is not None
        assert tweet.user_id == sample_user.id
        assert tweet.content == 'This is a test tweet'
        assert tweet.created_at is not None
        assert tweet.likes_count == 0


def test_tweet_to_dict(app, sample_user):
    """Test Tweet to_dict method."""
    with app.app_context():
        tweet = Tweet(
            user_id=sample_user.id,
            content='Test tweet content'
        )
        db.session.add(tweet)
        db.session.commit()
        
        tweet_dict = tweet.to_dict()
        assert tweet_dict['id'] == tweet.id
        assert tweet_dict['content'] == 'Test tweet content'
        assert 'attachments' in tweet_dict
        assert 'author' in tweet_dict
        assert 'likes' in tweet_dict


def test_follow_model(app, sample_users):
    """Test Follow model creation."""
    with app.app_context():
        follow = Follow(
            follower_id=sample_users[0].id,
            following_id=sample_users[1].id
        )
        db.session.add(follow)
        db.session.commit()
        
        assert follow.id is not None
        assert follow.follower_id == sample_users[0].id
        assert follow.following_id == sample_users[1].id
        assert follow.created_at is not None


def test_like_model(app, sample_user):
    """Test Like model creation."""
    with app.app_context():
        tweet = Tweet(
            user_id=sample_user.id,
            content='Test tweet'
        )
        db.session.add(tweet)
        db.session.commit()
        
        like = Like(
            user_id=sample_user.id,
            tweet_id=tweet.id
        )
        db.session.add(like)
        db.session.commit()
        
        assert like.id is not None
        assert like.user_id == sample_user.id
        assert like.tweet_id == tweet.id
        assert like.created_at is not None


def test_media_model(app):
    """Test Media model creation."""
    with app.app_context():
        media = Media(
            filename='test.jpg',
            original_filename='original_test.jpg',
            content_type='image/jpeg',
            file_size=1024
        )
        db.session.add(media)
        db.session.commit()
        
        assert media.id is not None
        assert media.filename == 'test.jpg'
        assert media.original_filename == 'original_test.jpg'
        assert media.content_type == 'image/jpeg'
        assert media.file_size == 1024
        assert media.get_url() == '/uploads/test.jpg'


def test_user_relationships(app, sample_users):
    """Test User model relationships."""
    with app.app_context():
        # Create follow relationship
        follow = Follow(
            follower_id=sample_users[0].id,
            following_id=sample_users[1].id
        )
        db.session.add(follow)
        
        # Create tweet and like
        tweet = Tweet(
            user_id=sample_users[1].id,
            content='Test tweet'
        )
        db.session.add(tweet)
        db.session.flush()
        
        like = Like(
            user_id=sample_users[0].id,
            tweet_id=tweet.id
        )
        db.session.add(like)
        db.session.commit()
        
        # Test relationships
        user1 = User.query.get(sample_users[0].id)
        user2 = User.query.get(sample_users[1].id)
        
        assert user1.following.count() == 1
        assert user2.followers.count() == 1
        assert user1.likes.count() == 1
        assert user2.tweets.count() == 1
