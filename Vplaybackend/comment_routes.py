from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson import ObjectId

comment_bp = Blueprint('comment_bp', __name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:6000/')
db = client['mydb']
videos_collection = db['videos']
comments_collection = db['comments']
users_collection=db['users']


@comment_bp.route('/comments/<video_id>', methods=['GET'])
def get_comments(video_id):
    comments = comments_collection.find({'video_id': video_id})
    comments_list = []
    for comment in comments:
        comments_list.append({
            'userId': comment['userId'],
            'text': comment['text']
        })
    return jsonify(comments_list), 200


@comment_bp.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    user_id = data['userID']
    comment_text = data['text']
    video_filename = data['video_filename']
    is_offensive = data['isOffensive']  # Get the offensive status from the request payload

    # Step 1: If offensive, update user's offensive count
    if is_offensive:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        # Initialize offensive_count if it doesn't exist
        offensive_count = user.get('offensive_count', 0)
        
        # Increment offensive count
        offensive_count += 1
        
        # Update offensive count in the database
        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'offensive_count': offensive_count}})
        
        # Send email to the user after 3 offensive comments
        if offensive_count == 3:
            user_email = user['email']
            send_email(user_email, 'Warning: Offensive Comments', 'You have posted 3 offensive comments. Please be cautious or your account will be removed.')
        
        # Remove user after 6 offensive comments
        if offensive_count >= 6:
            remove_user(user_id)  # Custom function to remove user and related data
            return jsonify({'message': 'User removed due to too many offensive comments'}), 200
    
    # Step 2: Add the comment to the database (with offensive status)
    new_comment = {
        'userID': user_id,
         'text': "This comment violated the Guidelines" if is_offensive else comment_text,
        'video_filename': video_filename,
        'isOffensive': is_offensive  # Ensure that 'isOffensive' field is included
    }
    
    new_comment = {
        'userID': user_id,
         'text': "This comment violated the Guidelines" if is_offensive else comment_text,
        'video_filename': video_filename,
        'isOffensive': is_offensive  # Ensure that 'isOffensive' field is included
    }
    

    print(new_comment)
    print("This is where",is_offensive)
    # Insert the new comment into the MongoDB collection
    inserted_comment = comments_collection.insert_one(new_comment)
    
    if inserted_comment:
        return jsonify({'message': 'Comment added successfully', 'comment': new_comment}), 200
    else:
        return jsonify({'message': 'Failed to add comment'}), 500
