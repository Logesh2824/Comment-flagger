from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from flask_cors import CORS

auth_bp = Blueprint('auth_bp', __name__)
CORS(auth_bp, supports_credentials=True)

# MongoDB connection
client = MongoClient('mongodb://localhost:6000/')
db = client['mydb']
users_collection = db['users']

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 400

    session['user_id'] = user['userId']
    session['username'] = user['name']

    return jsonify({
        'message': 'Login successful',
        'userId': user['userId'],
        'profilePicture': user.get('profilePicture'),
    }), 200

