from app import db
from datetime import datetime
from typing import List, Optional


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    api_key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tweets = db.relationship('Tweet', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Following relationships
    following = db.relationship(
        'Follow', 
        foreign_keys='Follow.follower_id',
        backref='follower', 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow', 
        foreign_keys='Follow.following_id',
        backref='followed', 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_followers: bool = True) -> dict:
        result = {
            'id': self.id,
            'name': self.username
        }
        
        if include_followers:
            result.update({
                'followers': [{'id': f.follower.id, 'name': f.follower.username} for f in self.followers],
                'following': [{'id': f.followed.id, 'name': f.followed.username} for f in self.following]
            })
        
        return result

    
class Tweet(db.Model):
    __tablename__ = 'tweets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    likes = db.relationship('Like', backref='tweet', lazy='dynamic', cascade='all, delete-orphan')
    media = db.relationship('Media', backref='tweet', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def likes_count(self) -> int:
        return self.likes.count()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'content': self.content,
            'attachments': [media.get_url() for media in self.media],
            'author': self.author.to_dict(include_followers=False),
            'likes': [{'user_id': like.user.id, 'name': like.user.username} for like in self.likes]
        }

    
class Follow(db.Model):
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id'),)

    
class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'tweet_id'),)


class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_url(self) -> str:
        return f'/uploads/{self.filename}'