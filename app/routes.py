from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import desc, func
from app import db
from app.models import User, Tweet, Follow, Like, Media
from flasgger import swag_from
import os
import uuid
from typing import Optional, Tuple, Dict, Any

api_bp = Blueprint('api', __name__)


def get_user_by_api_key(api_key: str) -> Optional[User]:
    """Get user by API key"""
    return User.query.filter_by(api_key=api_key).first()


def error_response(error_type: str, error_message: str, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """Return error response"""
    return {
        'result': False,
        'error_type': error_type,
        'error_message': error_message
    }, status_code


def success_response(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return success response"""
    response = {'result': True}
    if data:
        response.update(data)
    return response


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/tweets', methods=['POST'])
@swag_from({
    'tags': ['Tweets'],
    'summary': 'Create a new tweet',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        }
    ],
    'requestBody': {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'tweet_data': {
                            'type': 'string',
                            'description': 'Tweet content'
                        },
                        'tweet_media_ids': {
                            'type': 'array',
                            'items': {'type': 'integer'},
                            'description': 'Array of media IDs'
                        }
                    },
                    'required': ['tweet_data']
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Tweet created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'tweet_id': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'}
    }
})
def create_tweet():
    """Create a new tweet"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    data = request.get_json()
    if not data or 'tweet_data' not in data:
        return error_response('BAD_REQUEST', 'tweet_data is required')
    
    tweet_data = data['tweet_data'].strip()
    if not tweet_data:
        return error_response('BAD_REQUEST', 'Tweet content cannot be empty')
    
    if len(tweet_data) > 280:
        return error_response('BAD_REQUEST', 'Tweet content exceeds 280 characters')
    
    try:
        # Create tweet
        tweet = Tweet(user_id=user.id, content=tweet_data)
        db.session.add(tweet)
        db.session.flush()  # To get tweet ID
        
        # Associate media if provided
        media_ids = data.get('tweet_media_ids', [])
        if media_ids:
            media_objects = Media.query.filter(
                Media.id.in_(media_ids),
                Media.tweet_id.is_(None)
            ).all()
            
            for media in media_objects:
                media.tweet_id = tweet.id
        
        db.session.commit()
        return success_response({'tweet_id': tweet.id})
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/medias', methods=['POST'])
@swag_from({
    'tags': ['Media'],
    'summary': 'Upload media file',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        }
    ],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Image file to upload'
        }
    ],
    'responses': {
        200: {
            'description': 'File uploaded successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'media_id': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'}
    }
})
def upload_media():
    """Upload media file"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    if 'file' not in request.files:
        return error_response('BAD_REQUEST', 'No file provided')
    
    file = request.files['file']
    if file.filename == '':
        return error_response('BAD_REQUEST', 'No file selected')
    
    if not allowed_file(file.filename):
        return error_response('BAD_REQUEST', 'File type not allowed. Only images are allowed.')
    
    try:
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Save media record
        media = Media(
            filename=filename,
            original_filename=file.filename,
            content_type=file.content_type,
            file_size=os.path.getsize(filepath)
        )
        db.session.add(media)
        db.session.commit()
        
        return success_response({'media_id': media.id})
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/tweets/<int:tweet_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Tweets'],
    'summary': 'Delete a tweet',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        },
        {
            'name': 'tweet_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Tweet ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Tweet deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden'},
        404: {'description': 'Tweet not found'}
    }
})
def delete_tweet(tweet_id: int):
    """Delete a tweet"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    tweet = Tweet.query.get(tweet_id)
    if not tweet:
        return error_response('NOT_FOUND', 'Tweet not found', 404)
    
    if tweet.user_id != user.id:
        return error_response('FORBIDDEN', 'You can only delete your own tweets', 403)
    
    try:
        # Delete associated media files
        for media in tweet.media:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], media.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(tweet)
        db.session.commit()
        return success_response()
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/tweets/<int:tweet_id>/likes', methods=['POST'])
@swag_from({
    'tags': ['Likes'],
    'summary': 'Like a tweet',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        },
        {
            'name': 'tweet_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Tweet ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Tweet liked successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Tweet not found'}
    }
})
def like_tweet(tweet_id: int):
    """Like a tweet"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    tweet = Tweet.query.get(tweet_id)
    if not tweet:
        return error_response('NOT_FOUND', 'Tweet not found', 404)
    
    # Check if already liked
    existing_like = Like.query.filter_by(user_id=user.id, tweet_id=tweet_id).first()
    if existing_like:
        return success_response()  # Already liked, return success
    
    try:
        like = Like(user_id=user.id, tweet_id=tweet_id)
        db.session.add(like)
        db.session.commit()
        return success_response()
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/tweets/<int:tweet_id>/likes', methods=['DELETE'])
@swag_from({
    'tags': ['Likes'],
    'summary': 'Unlike a tweet',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        },
        {
            'name': 'tweet_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Tweet ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Tweet unliked successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Tweet not found'}
    }
})
def unlike_tweet(tweet_id: int):
    """Unlike a tweet"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    tweet = Tweet.query.get(tweet_id)
    if not tweet:
        return error_response('NOT_FOUND', 'Tweet not found', 404)
    
    like = Like.query.filter_by(user_id=user.id, tweet_id=tweet_id).first()
    if not like:
        return success_response()  # Not liked, return success
    
    try:
        db.session.delete(like)
        db.session.commit()
        return success_response()
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/users/<int:user_id>/follow', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Follow a user',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID to follow'
        }
    ],
    'responses': {
        200: {
            'description': 'User followed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
})
def follow_user(user_id: int):
    """Follow a user"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    if user.id == user_id:
        return error_response('BAD_REQUEST', 'Cannot follow yourself')
    
    target_user = User.query.get(user_id)
    if not target_user:
        return error_response('NOT_FOUND', 'User not found', 404)
    
    # Check if already following
    existing_follow = Follow.query.filter_by(follower_id=user.id, following_id=user_id).first()
    if existing_follow:
        return success_response()  # Already following
    
    try:
        follow = Follow(follower_id=user.id, following_id=user_id)
        db.session.add(follow)
        db.session.commit()
        return success_response()
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/users/<int:user_id>/follow', methods=['DELETE'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Unfollow a user',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        },
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID to unfollow'
        }
    ],
    'responses': {
        200: {
            'description': 'User unfollowed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'}
                }
            }
        },
        400: {'description': 'Bad request'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'User not found'}
    }
})
def unfollow_user(user_id: int):
    """Unfollow a user"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    target_user = User.query.get(user_id)
    if not target_user:
        return error_response('NOT_FOUND', 'User not found', 404)
    
    follow = Follow.query.filter_by(follower_id=user.id, following_id=user_id).first()
    if not follow:
        return success_response()  # Not following
    
    try:
        db.session.delete(follow)
        db.session.commit()
        return success_response()
    
    except Exception as e:
        db.session.rollback()
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/tweets', methods=['GET'])
@swag_from({
    'tags': ['Tweets'],
    'summary': 'Get tweet feed',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        }
    ],
    'responses': {
        200: {
            'description': 'Tweet feed retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'tweets': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'content': {'type': 'string'},
                                'attachments': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                },
                                'author': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'}
                                    }
                                },
                                'likes': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'user_id': {'type': 'integer'},
                                            'name': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {'description': 'Unauthorized'}
    }
})
def get_tweets():
    """Get tweet feed sorted by popularity"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    try:
        # Get IDs of users that current user follows
        following_ids = db.session.query(Follow.following_id).filter_by(follower_id=user.id).subquery()
        
        # Get tweets from followed users, ordered by likes count (popularity) descending
        tweets = db.session.query(Tweet, func.count(Like.id).label('likes_count'))\
            .outerjoin(Like)\
            .filter(Tweet.user_id.in_(following_ids))\
            .group_by(Tweet.id)\
            .order_by(desc('likes_count'), desc(Tweet.created_at))\
            .all()
        
        # Convert to dictionary format
        tweet_list = []
        for tweet, _ in tweets:
            tweet_list.append(tweet.to_dict())
        
        return success_response({'tweets': tweet_list})
    
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/users/me', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get current user profile',
    'parameters': [
        {
            'name': 'api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User API key'
        }
    ],
    'responses': {
        200: {
            'description': 'User profile retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'followers': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            },
                            'following': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {'description': 'Unauthorized'}
    }
})
def get_current_user():
    """Get current user profile"""
    api_key = request.headers.get('api-key')
    if not api_key:
        return error_response('UNAUTHORIZED', 'API key is required', 401)
    
    user = get_user_by_api_key(api_key)
    if not user:
        return error_response('UNAUTHORIZED', 'Invalid API key', 401)
    
    return success_response({'user': user.to_dict()})


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get user profile by ID',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'User ID'
        }
    ],
    'responses': {
        200: {
            'description': 'User profile retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'followers': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            },
                            'following': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'name': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'User not found'}
    }
})
def get_user_by_id(user_id: int):
    """Get user profile by ID"""
    user = User.query.get(user_id)
    if not user:
        return error_response('NOT_FOUND', 'User not found', 404)
    
    return success_response({'user': user.to_dict()})


# Route to serve uploaded files
@api_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Login endpoint for API compatibility  
@api_bp.route('/login', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Frontend login compatibility',
    'description': 'Returns available API keys for testing',
    'responses': {
        200: {
            'description': 'Available API keys',
            'schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'api_keys': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'username': {'type': 'string'},
                                'api_key': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def login_compatibility():
    """Login endpoint for frontend compatibility"""
    try:
        # Get all users with their API keys
        users = User.query.all()
        api_keys = [
            {
                'username': user.username,
                'api_key': user.api_key
            }
            for user in users
        ]
        
        return {
            'result': True,
            'message': 'Use one of these API keys for authentication',
            'api_keys': api_keys
        }
    
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)
