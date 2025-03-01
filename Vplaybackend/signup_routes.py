from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from flask_cors import CORS
import base64
import uuid  # Import the uuid module

signup_bp = Blueprint('signup_bp', __name__)
CORS(signup_bp, supports_credentials=True)

client = MongoClient('mongodb://localhost:6000/')
db = client['mydb']
users_collection = db['users']

@signup_bp.route('/signup', methods=['POST'])
def signup():
    # Generate a new user ID using UUID
    user_id = str(uuid.uuid4())
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    profile_picture = request.files.get('profilePicture')

    # Check if the email already exists in the database
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already exists'}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Convert the profile picture to base64 if it exists
    profile_picture_base64 = base64.b64encode(profile_picture.read()).decode('utf-8') if profile_picture else None

    # Create a new user document
    user = {
        'userId': user_id,  # Use the generated UUID
        'name': name,
        'email': email,
        'password': hashed_password,
        'profilePicture': profile_picture_base64,
        'subscribedUsers': [],
        'followers': []
    }

    # Insert the new user into the users collection
    users_collection.insert_one(user)
    
    return jsonify({'message': 'Signup successful'}), 201
