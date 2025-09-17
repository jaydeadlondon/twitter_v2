from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), Optional=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), Optional=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)

    
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)