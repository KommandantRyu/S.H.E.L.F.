from flask import Blueprint, request, jsonify, session
from models.auth import validate_user
from models.admin.user_models import create_user  
from db import get_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the Library Management System'})

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = 'user' 
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    success, message = create_user(username, email, password, role)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message}), 201

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    user = validate_user(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    # store user info in session
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    session['role'] = user['role']
    return jsonify({'message': 'Login successful', 'user': user}), 200

@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200