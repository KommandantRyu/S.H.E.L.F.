from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from models.auth import validate_user
from models.user.user_model import register_user 
from routes.user_routes import user_bp

main_bp = Blueprint('main', __name__)

main_bp.register_blueprint(user_bp)

@main_bp.route('/registration_page')
def registration_page():
    return render_template('registration.html')

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not all([name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    success, message = register_user(name, email, password,)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'successful': message}),200

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