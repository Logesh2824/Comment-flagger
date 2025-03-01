from flask import Blueprint, request, jsonify, send_file, session
from gridfs import GridFS
from pymongo import MongoClient
import base64

client = MongoClient('mongodb://localhost:6000/')
db = client['mydb']
fs = GridFS(db)
videos_collection = db['videos']
users_collection = db['users']

video_bp = Blueprint('video_bp', __name__)

@video_bp.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files or 'thumbnail' not in request.files:
        return 'Video and thumbnail are required', 400

    title = request.form.get('title')
    description = request.form.get('description')
    owner_id = session.get('user_id')
    print(f"Current user ID from session: {owner_id}")

    video_file = request.files['video']
    thumbnail_file = request.files['thumbnail']

    # Store thumbnail as base64
    thumbnail_base64 = base64.b64encode(thumbnail_file.read()).decode('utf-8')

    # Retrieve user's email from the users collection
    user = users_collection.find_one({'userId': owner_id})
    if not user:
        return 'User not found', 404

    email = user['email']  # Assuming the users collection has an 'email' field

    # Create a new filename with email and original filename
    new_filename = f"{email}_{video_file.filename}"

    # Store video in GridFS
    file_id = fs.put(video_file, filename=new_filename, contentType='video/mp4')

    video = {
        'ownerId': owner_id,
        'title': title,
        'description': description,
        'filename': new_filename,  # Store the new filename
        'thumbnail': thumbnail_base64,
        'file_id': file_id,
        'likes': [],
        'comments': []
    }
    
    videos_collection.insert_one(video)
    return jsonify({'message': 'Video uploaded successfully'}), 201
@video_bp.route('/videos', methods=['GET'])
def get_videos():
    videos = videos_collection.find()
    video_list = []
    for video in videos:
        owner = users_collection.find_one({'userId': video['ownerId']})
        video_list.append({
            'ownerId':video['ownerId'],
            'title': video['title'],
            'thumbnail': video['thumbnail'],
            'filename': video['filename'],
            'ownerName': owner['name'],
            'ownerProfilePicture': owner['profilePicture']
        })
    return jsonify(video_list)

@video_bp.route('/video/<filename>', methods=['GET'])
def get_video(filename):
    file = fs.find_one({'filename': filename})
    if not file:
        return 'File not found', 404
    
    current_user_id = session.get('user_id')
    if not current_user_id:
        return 'User not logged in', 403

    # Add the filename to the user's watch history (if not already present)
    users_collection.update_one(
        {'userId': current_user_id},
        {'$addToSet': {'history': filename}}  # $addToSet ensures no duplicates
    )

    return send_file(file, mimetype='video/mp4')
@video_bp.route('/subscribed_videos', methods=['GET'])
def get_subscribed_videos():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return 'User not logged in', 403

    # Get the current user and their subscriptions
    current_user = users_collection.find_one({'userId': current_user_id})
    if not current_user or 'subscribedUsers' not in current_user:
        return jsonify([])  # Return an empty list if no subscriptions

    subscribed_users = current_user['subscribedUsers']  # This should be an array of user IDs

    # Fetch videos from subscribed users
    videos = videos_collection.find({'ownerId': {'$in': subscribed_users}})
    video_list = []
    
    for video in videos:
        owner = users_collection.find_one({'userId': video['ownerId']})
        video_list.append({
            'ownerId': video['ownerId'],
            'title': video['title'],
            'thumbnail': video['thumbnail'],
            'filename': video['filename'],
            'ownerName': owner['name'],
            'ownerProfilePicture': owner['profilePicture'],
            'file_id': str(video['_id']),    # Include file_id for the VideoCard
        })

    return jsonify(video_list)
@video_bp.route('/my_page', methods=['GET'])
def my_page():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return 'User not logged in', 403

    # Get user details
    user = users_collection.find_one({'userId': current_user_id})
    if not user:
        return 'User not found', 404

    # Get user's uploaded videos
    videos = videos_collection.find({'ownerId': current_user_id})
    video_list = []
    
    for video in videos:
        video_list.append({
            'title': video['title'],
            'thumbnail': video['thumbnail'],
            'file_id': str(video['_id']), 
            'filename':video['filename'], # Include file_id for deletion
        })

    return jsonify({
        'username': user['name'],
        'email': user['email'],
        'profilePicture': user['profilePicture'],
        'videos': video_list
    })

@video_bp.route('/delete_video', methods=['DELETE'])
def delete_video():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return 'User not logged in', 403

    filename = request.json.get('filename')
    print(f"Attempting to delete video with filename: {filename}")  # Get the filename from the request
    if not filename:
        return 'Filename is required', 400

    # Find the video by filename and owner ID
    video = videos_collection.find_one({'filename': filename, 'ownerId': current_user_id})
    if not video:
        return 'Video not found or does not belong to the user', 404

    # Delete video from GridFS
    fs.delete(video['file_id'])
    
    # Delete video document from the collection
    videos_collection.delete_one({'_id': video['_id']})

    return jsonify({'message': 'Video deleted successfully'}), 200
@video_bp.route('/watch_history', methods=['GET'])
def get_watch_history():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return 'User not logged in', 403

    # Fetch user's history
    user = users_collection.find_one({'userId': current_user_id})
    if not user or 'history' not in user:
        return jsonify([])  # Return an empty list if no history

    history_filenames = user['history']

    # Fetch videos based on filenames stored in history
    videos = videos_collection.find({'filename': {'$in': history_filenames}})
    video_list = []

    for video in videos:
        owner = users_collection.find_one({'userId': video['ownerId']})
        video_list.append({
            'ownerId': video['ownerId'],
            'title': video['title'],
            'thumbnail': video['thumbnail'],
            'filename': video['filename'],
            'ownerName': owner['name'],
            'ownerProfilePicture': owner['profilePicture'],
            'file_id': str(video['_id']),  # Include file_id for VideoCard
        })

    return jsonify(video_list)
@video_bp.route('/search', methods=['GET'])
def search_videos():
    query = request.args.get('query')
    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    # Find videos where the title contains the query (case-insensitive)
    videos = videos_collection.find({'title': {'$regex': query, '$options': 'i'}})
    video_list = []

    for video in videos:
        owner = users_collection.find_one({'userId': video['ownerId']})
        video_list.append({
            'ownerId': video['ownerId'],
            'title': video['title'],
            'thumbnail': video['thumbnail'],
            'filename': video['filename'],
            'ownerName': owner['name'],
            'ownerProfilePicture': owner['profilePicture'],
            'file_id': str(video['_id']),  # Include file_id for VideoCard
        })

    return jsonify(video_list)

@video_bp.route('/user/<user_id>/offensive_count', methods=['GET'])
def get_offensive_count(user_id):
    user = users_collection.find_one({'userId': user_id}, {'offensive_comments_count': 1})
    if user:
        return jsonify({'offensive_count': user.get('offensive_comments_count', 0)})
    return jsonify({'offensive_count': 0})


