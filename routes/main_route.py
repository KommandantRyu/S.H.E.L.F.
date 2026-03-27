from flask import Blueprint, request, jsonify, session
from models.auth import validate_user
from models.admin.user_models import create_user  

main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = 'user' 
    if not all([name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    success, message = create_user(name, email, password, role)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message}), 201

@main_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user = validate_user(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user_id'] = user['user_id']
    session['email'] = user['email']
    return jsonify({'message': 'Login successful', 'user': user}), 200

@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200