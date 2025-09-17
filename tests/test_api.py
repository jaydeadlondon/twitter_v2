import json
import pytest
from app import db
from app.models import User, Tweet, Follow, Like


class TestTweetAPI:
    """Test tweet-related API endpoints."""
    
    def test_create_tweet_success(self, client, sample_user):
        """Test successful tweet creation."""
        response = client.post(
            '/api/tweets',
            json={'tweet_data': 'This is a test tweet'},
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
        assert 'tweet_id' in data
    
    def test_create_tweet_without_api_key(self, client):
        """Test tweet creation without API key."""
        response = client.post(
            '/api/tweets',
            json={'tweet_data': 'This is a test tweet'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'UNAUTHORIZED'
    
    def test_create_tweet_invalid_api_key(self, client):
        """Test tweet creation with invalid API key."""
        response = client.post(
            '/api/tweets',
            json={'tweet_data': 'This is a test tweet'},
            headers={'api-key': 'invalid-key'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'UNAUTHORIZED'
    
    def test_create_tweet_empty_content(self, client, sample_user):
        """Test tweet creation with empty content."""
        response = client.post(
            '/api/tweets',
            json={'tweet_data': ''},
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'BAD_REQUEST'
    
    def test_create_tweet_too_long(self, client, sample_user):
        """Test tweet creation with content too long."""
        long_content = 'x' * 281  # Exceeds 280 character limit
        response = client.post(
            '/api/tweets',
            json={'tweet_data': long_content},
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'BAD_REQUEST'
    
    def test_delete_tweet_success(self, client, sample_user, app):
        """Test successful tweet deletion."""
        with app.app_context():
            # Create a tweet first
            tweet = Tweet(user_id=sample_user.id, content='Test tweet')
            db.session.add(tweet)
            db.session.commit()
            tweet_id = tweet.id
        
        response = client.delete(
            f'/api/tweets/{tweet_id}',
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
    
    def test_delete_nonexistent_tweet(self, client, sample_user):
        """Test deleting non-existent tweet."""
        response = client.delete(
            '/api/tweets/999999',
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'NOT_FOUND'
    
    def test_get_tweets_success(self, client, sample_users, app):
        """Test getting tweet feed."""
        with app.app_context():
            # Create follow relationship
            follow = Follow(
                follower_id=sample_users[0].id,
                following_id=sample_users[1].id
            )
            db.session.add(follow)
            
            # Create tweet from followed user
            tweet = Tweet(
                user_id=sample_users[1].id,
                content='Tweet from followed user'
            )
            db.session.add(tweet)
            db.session.commit()
        
        response = client.get(
            '/api/tweets',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
        assert 'tweets' in data


class TestLikeAPI:
    """Test like-related API endpoints."""
    
    def test_like_tweet_success(self, client, sample_users, app):
        """Test successful tweet liking."""
        with app.app_context():
            tweet = Tweet(
                user_id=sample_users[1].id,
                content='Test tweet'
            )
            db.session.add(tweet)
            db.session.commit()
            tweet_id = tweet.id
        
        response = client.post(
            f'/api/tweets/{tweet_id}/likes',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
    
    def test_unlike_tweet_success(self, client, sample_users, app):
        """Test successful tweet unliking."""
        with app.app_context():
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
            tweet_id = tweet.id
        
        response = client.delete(
            f'/api/tweets/{tweet_id}/likes',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True


class TestUserAPI:
    """Test user-related API endpoints."""
    
    def test_get_current_user(self, client, sample_user):
        """Test getting current user profile."""
        response = client.get(
            '/api/users/me',
            headers={'api-key': 'test-api-key-123'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
        assert 'user' in data
        assert data['user']['name'] == 'testuser'
    
    def test_get_user_by_id(self, client, sample_user):
        """Test getting user profile by ID."""
        response = client.get(f'/api/users/{sample_user.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
        assert 'user' in data
        assert data['user']['id'] == sample_user.id
    
    def test_follow_user_success(self, client, sample_users):
        """Test successful user following."""
        response = client.post(
            f'/api/users/{sample_users[1].id}/follow',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
    
    def test_follow_self_error(self, client, sample_users):
        """Test error when trying to follow yourself."""
        response = client.post(
            f'/api/users/{sample_users[0].id}/follow',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['result'] is False
        assert data['error_type'] == 'BAD_REQUEST'
    
    def test_unfollow_user_success(self, client, sample_users, app):
        """Test successful user unfollowing."""
        with app.app_context():
            follow = Follow(
                follower_id=sample_users[0].id,
                following_id=sample_users[1].id
            )
            db.session.add(follow)
            db.session.commit()
        
        response = client.delete(
            f'/api/users/{sample_users[1].id}/follow',
            headers={'api-key': 'alice-key'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is True
