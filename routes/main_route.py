from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from models.auth import validate_user
from models.user.user_model import register_user
from models.admin.book_models import get_all_books

main_bp = Blueprint('main', __name__)


def _session_user_payload(user_row):
    if not user_row:
        return None
    return {
        'user_id': user_row['user_id'],
        'username': user_row.get('username'),
        'email': user_row.get('email'),
        'created_at': user_row['created_at'].isoformat()
        if user_row.get('created_at')
        else None,
    }


@main_bp.route('/registration_page')
def registration_page():
    return render_template('registration.html')


@main_bp.route('/about')
def about_page():
    return render_template('about.html')


@main_bp.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please sign in to browse the catalog.', 'error')
        return redirect(url_for('landing_page'))
    books = get_all_books()
    if books is None:
        flash(
            'The catalog could not be loaded. Check that MySQL is running, '
            'your credentials in environment variables are correct, and the '
            '`books` table exists.',
            'error',
        )
        books = []
    return render_template('home.html', books=books)


@main_bp.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    name = data.get('name') or data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not all([name, email, password]):
        if request.is_json:
            return jsonify({'error': 'Missing required fields'}), 400
        flash('Please fill in name, email, and password.', 'error')
        return redirect(url_for('main.registration_page'))

    success, message = register_user(name, email, password)
    if not success:
        if request.is_json:
            return jsonify({'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('main.registration_page'))

    if request.is_json:
        return jsonify({'success': True, 'message': message}), 200
    flash('Account created. You can sign in now.', 'success')
    return redirect(url_for('landing_page'))


@main_bp.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        email = data.get('email') or data.get('username')
        password = data.get('password')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

    if not email or not password:
        if request.is_json:
            return jsonify({'error': 'Email and password required'}), 400
        flash('Email and password are required.', 'error')
        return redirect(url_for('landing_page'))

    user = validate_user(email, password)
    if not user:
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid email or password.', 'error')
        return redirect(url_for('landing_page'))

    session['user_id'] = user['user_id']
    session['email'] = user['email']
    session['username'] = user.get('username', '')

    if request.is_json:
        return jsonify({'message': 'Login successful', 'user': _session_user_payload(user)}), 200
    return redirect(url_for('main.home'))


@main_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    wants_json = (
        request.is_json
        or 'application/json' in (request.headers.get('Accept') or '')
        or request.args.get('format') == 'json'
    )
    if wants_json:
        return jsonify({'message': 'Logged out successfully'}), 200
    flash('You have been signed out.', 'success')
    return redirect(url_for('landing_page'))
