from flask import Blueprint, request, jsonify, session
from models.user.user_model import (
    get_user_profile, update_user_profile,
    get_user_borrowed_books, get_user_borrowing_history, get_user_purchased_books
)
from models.admin.book_models import (
    borrow_book, return_book, purchase_book, get_all_books, sort_books, get_book_by_id
)

user_bp = Blueprint('user', __name__, url_prefix='/user')

def login_required():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return None

# Profile
@user_bp.route('/profile', methods=['GET'])
def profile():
    err = login_required()
    if err: return err
    user_id = session['user_id']
    profile = get_user_profile(user_id)
    if not profile:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(profile)

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    err = login_required()
    if err: return err
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    success, message = update_user_profile(user_id, username, email, password)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message})

# Books (viewing)
@user_bp.route('/books', methods=['GET'])
def list_books():
    err = login_required()
    if err: return err
    sort_by = request.args.get('sort_by')
    order = request.args.get('order')
    books = sort_books(sort_by, order) if sort_by or order else get_all_books()
    if books is None:
        return jsonify({'error': 'Failed to fetch books'}), 500
    return jsonify(books)

@user_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    err = login_required()
    if err: return err
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)

# Borrowing
@user_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow(book_id):
    err = login_required()
    if err: return err
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    borrow_date = data.get('borrow_date')
    due_date = data.get('due_date')
    if not borrow_date or not due_date:
        return jsonify({'error': 'Missing borrow_date or due_date'}), 400
    success, message = borrow_book(book_id, user_id, borrow_date, due_date)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message}), 200

@user_bp.route('/books/<int:book_id>/return', methods=['POST'])
def return_book_route(book_id):
    err = login_required()
    if err: return err
    data = request.get_json(silent=True) or {}
    return_date = data.get('return_date')
    if not return_date:
        return jsonify({'error': 'Missing return_date'}), 400
    success, message = return_book(book_id, return_date, user_id=session['user_id'])
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message}), 200

# Purchase
@user_bp.route('/books/<int:book_id>/purchase', methods=['POST'])
def purchase(book_id):
    err = login_required()
    if err: return err
    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    purchase_date = data.get('purchase_date')
    price_paid = data.get('price_paid')
    if not purchase_date or not price_paid:
        return jsonify({'error': 'Missing purchase_date or price_paid'}), 400
    success, message = purchase_book(book_id, user_id, purchase_date, price_paid)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message}), 200

# History
@user_bp.route('/borrowed', methods=['GET'])
def borrowed_books():
    err = login_required()
    if err: return err
    user_id = session['user_id']
    books = get_user_borrowed_books(user_id)
    if books is None:
        return jsonify({'error': 'Failed to fetch borrowed books'}), 500
    return jsonify(books)

@user_bp.route('/history', methods=['GET'])
def borrowing_history():
    err = login_required()
    if err: return err
    user_id = session['user_id']
    history = get_user_borrowing_history(user_id)
    if history is None:
        return jsonify({'error': 'Failed to fetch history'}), 500
    return jsonify(history)

@user_bp.route('/purchases', methods=['GET'])
def purchase_history():
    err = login_required()
    if err: return err
    user_id = session['user_id']
    purchases = get_user_purchased_books(user_id)
    if purchases is None:
        return jsonify({'error': 'Failed to fetch purchases'}), 500
    return jsonify(purchases)