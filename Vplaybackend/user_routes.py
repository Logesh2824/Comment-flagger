from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson import ObjectId
# Initialize Flask extensions
client = MongoClient('mongodb://localhost:6000/')
db = client['mydb']  # Replace with your database name
users_collection = db.users
videos_collection = db.videos
comments_collection = db.comments
files_collection = db.fs.files  # Metadata for files
chunks_collection = db.fs.chunks

user_bp = Blueprint('user_bp', __name__)

# Route for subscribing to a user
@user_bp.route('/subscribe/<owner_id>', methods=['POST'])
def subscribe_user(owner_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 401

    # Add userId to the followers array of the ownerId
    users_collection.update_one(
        {'userId': owner_id},
        {'$addToSet': {'followers': user_id}}  # Use $addToSet to avoid duplicates
    )

    # Add ownerId to the subscribedUsers array of the current user
    users_collection.update_one(
        {'userId': user_id},
        {'$addToSet': {'subscribedUsers': owner_id}}  # Add ownerId to subscribedUsers
    )

    return jsonify({'message': 'Subscribed successfully'}), 200

# Route for unsubscribing from a user
@user_bp.route('/unsubscribe/<owner_id>', methods=['POST'])
def unsubscribe_user(owner_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 401

    # Remove userId from the followers array of the ownerId
    users_collection.update_one(
        {'userId': owner_id},
        {'$pull': {'followers': user_id}}  # Use $pull to remove the user ID
    )

    # Remove ownerId from the subscribedUsers array of the current user
    users_collection.update_one(
        {'userId': user_id},
        {'$pull': {'subscribedUsers': owner_id}}  # Remove ownerId from subscribedUsers
    )

    return jsonify({'message': 'Unsubscribed successfully'}), 200

# Route for checking user information
@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user_info(user_id):
    user = users_collection.find_one({'userId': user_id})
    if user:
        return jsonify({
            'userId': user['userId'],
            'name': user['name'],
            'followers': user['followers'],
            'subscribed_users': user['subscribedUsers']
        }), 200
    return jsonify({'message': 'User not found'}), 404

# Route for getting current user ID
@user_bp.route('/current_user_id', methods=['GET'])
def get_current_user_id():
    user_id1 = session.get('user_id')
    print(f"Current user ID from session: {user_id1}")
    if user_id1:
        return jsonify({'userId': user_id1}), 200
    return jsonify({'message': 'User not logged in'}), 401

@user_bp.route('/users2/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({'userId': user_id})
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'name': user['name'],
        'profilePicture': user['profilePicture']
    }), 200


@user_bp.route('/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    
    # Extract required fields from the request data
    commentID = data.get('commentID')
    userID = data.get('userID')
    commentText = data.get('text')
    video_filename = data.get('video_filename')
    is_offensive = data.get('is_offensive', False)  # Default to False if not provided
    
    # Ensure required fields are present
    if not all([commentID, userID, commentText, video_filename]):
        return jsonify({'message': 'Missing required fields'}), 400

    # Create the comment object
    comment = {
        'commentID': commentID,
        'userID': userID,
        'commentText': commentText,
        'is_offensive': is_offensive  # Store the offensive status
    }

    # Insert the new comment into the comments collection
    comments_collection.insert_one(comment)

    # Update the corresponding video document by adding the commentID to its comments array
    videos_collection.update_one(
        {'filename': video_filename},
        {'$addToSet': {'comments': commentID}}  # Add commentID to the comments array
    )

    if is_offensive:
        users_collection.update_one(
            {'userId': userID},  # Assuming userID is stored as an ObjectId
            {'$inc': {'offensive_comments_count': 1}}  # Increment the offensive comments count
        )
    user = users_collection.find_one({'userId':userID})
    offensive_count = user.get('offensive_comments_count', 0)

    # Check if the offensive count exceeds 3
    if offensive_count > 6:
        return jsonify({'message': 'Your account is to be deleted as you have uploaded more than 6 offensive comments.Please log out now!!!!'}), 201

    if offensive_count > 3:
        return jsonify({'message': 'You have added three offensive comments'}), 201
    
    
    return jsonify({'message': 'Comment added successfully'}), 201


@user_bp.route('/comments/<comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = comments_collection.find_one({'commentID': comment_id})
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404
    comment['_id'] = str(comment['_id'])
    return jsonify(comment), 200
@user_bp.route('/like_video/<filename>', methods=['POST'])
def like_video(filename):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 401

    try:
        # Add userId to the likes array of the video document
        videos_collection.update_one(
            {'filename': filename},
            {'$addToSet': {'likes': user_id}}  # $addToSet avoids duplicate entries
        )
        return jsonify({'message': 'Video liked successfully'}), 200
    except Exception as e:
        print(f"Error liking video: {e}")
        return jsonify({'message': 'Failed to like video'}), 500

@user_bp.route('/unlike_video/<filename>', methods=['POST'])
def unlike_video(filename):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 401

    try:
        # Remove userId from the likes array of the video document
        videos_collection.update_one(
            {'filename': filename},
            {'$pull': {'likes': user_id}}  # $pull removes the user ID
        )
        return jsonify({'message': 'Video unliked successfully'}), 200
    except Exception as e:
        print(f"Error unliking video: {e}")
        return jsonify({'message': 'Failed to unlike video'}), 500
    


@user_bp.route('/video1/<filename>', methods=['GET'])
def get_video_details(filename):
    try:
        video_data = videos_collection.find_one({'filename': filename})
        if not video_data:
            return jsonify({'message': 'Video not found'}), 404

        user_id = session.get('user_id')
        liked_by_user = user_id in video_data.get('likes', []) if user_id else False
        like_count = len(video_data.get('likes', []))

        return jsonify({
            'ownerId': video_data['ownerId'],
            'title': video_data['title'],
            'commentIDs': video_data['comments'],
            'description': video_data['description'],
            'filename': filename,
            'likeCount': like_count,
            'likedByUser': liked_by_user
        }), 200
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return jsonify({'message': 'Failed to fetch video details'}), 500