from app import create_app, db
from app.models import User, Tweet, Follow, Like, Media
from config import get_config
import os


def create_sample_data():
    if User.query.first():
        return
    
    # sample users
    users_data = [
        {'username': 'alice', 'email': 'alice@example.com', 'api_key': 'alice-key-123'},
        {'username': 'bob', 'email': 'bob@example.com', 'api_key': 'bob-key-456'},
        {'username': 'charlie', 'email': 'charlie@example.com', 'api_key': 'charlie-key-789'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    
    # sample tweets
    tweets_data = [
        {'user_id': users[0].id, 'content': 'Hello world! This is my first tweet.'},
        {'user_id': users[0].id, 'content': 'Beautiful day today! 🌞'},
        {'user_id': users[1].id, 'content': 'Working on some exciting projects!'},
        {'user_id': users[1].id, 'content': 'Love this new Twitter clone! Great work team.'},
        {'user_id': users[2].id, 'content': 'Just deployed a new feature. Feeling proud!'},
    ]
    
    tweets = []
    for tweet_data in tweets_data:
        tweet = Tweet(**tweet_data)
        db.session.add(tweet)
        tweets.append(tweet)
    
    db.session.commit()
    
    follows_data = [
        {'follower_id': users[0].id, 'following_id': users[1].id},
        {'follower_id': users[0].id, 'following_id': users[2].id},
        {'follower_id': users[1].id, 'following_id': users[0].id},
        {'follower_id': users[2].id, 'following_id': users[0].id},
    ]
    
    for follow_data in follows_data:
        follow = Follow(**follow_data)
        db.session.add(follow)
    
    likes_data = [
        {'user_id': users[1].id, 'tweet_id': tweets[0].id},
        {'user_id': users[2].id, 'tweet_id': tweets[0].id},
        {'user_id': users[0].id, 'tweet_id': tweets[2].id},
        {'user_id': users[0].id, 'tweet_id': tweets[4].id},
    ]
    
    for like_data in likes_data:
        like = Like(**like_data)
        db.session.add(like)
    
    db.session.commit()
    print("Sample data created successfully!")


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # sample data if in development
        if app.config.get('ENV') != 'production':
            create_sample_data()
        
        print("Database initialized successfully!")
        
        users = User.query.all()
        if users:
            print("\nAvailable API keys for testing:")
            for user in users:
                print(f"  {user.username}: {user.api_key}")
    
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)