# admin_routes.py
from flask import Blueprint, request, jsonify
from models.admin.book_models import (
    get_all_books, update_book, delete_book, sort_books,
    borrow_book, return_book, purchase_book,
    create_book, get_book_by_id
)
from models.admin.user_models import (
    get_all_users, get_user_by_id, create_user, update_user, delete_user,
    update_user_role, sort_users
)
from db import get_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    users = get_all_users()
    books = get_all_books()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM borrowed_books WHERE return_date IS NULL")
    active_borrows = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        'total_users': len(users) if users else 0,
        'total_books': len(books) if books else 0,
        'active_borrows': active_borrows
    })


@admin_bp.route('/users', methods=['GET'])
def list_users():
    sort_by = request.args.get('sort_by')
    order = request.args.get('order')
    users = sort_users(sort_by, order) if sort_by or order else get_all_users()
    if users is None:
        return jsonify({'error': 'Failed to fetch users'}), 500
    return jsonify(users)

@admin_bp.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    success, message = create_user(username, email, password, role)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 201)

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    data = request.get_json()
    success, message = update_user(
        user_id,
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        role=data.get('role')
    )
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    success, message = delete_user(user_id)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)

@admin_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
def change_user_role(user_id):
    new_role = request.get_json().get('role')
    if not new_role:
        return jsonify({'error': 'Missing role'}), 400
    success, message = update_user_role(user_id, new_role)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)

# Books
@admin_bp.route('/books', methods=['GET'])
def list_books():
    sort_by = request.args.get('sort_by')
    order = request.args.get('order')
    books = sort_books(sort_by, order) if sort_by or order else get_all_books()
    if books is None:
        return jsonify({'error': 'Failed to fetch books'}), 500
    return jsonify(books)

@admin_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    required = ['title', 'author', 'genre', 'year', 'pages', 'isbn']
    if not all(k in data for k in required):
        return jsonify({'error': f'Missing fields: {", ".join(required)}'}), 400
    success, message = create_book(
        data['title'], data['author'], data['genre'],
        data['year'], data['pages'], data['isbn']
    )
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 201)

@admin_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)

@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
def edit_book(book_id):
    data = request.get_json()
    existing = get_book_by_id(book_id)
    if not existing:
        return jsonify({'error': 'Book not found'}), 404

    title = data.get('title', existing[1])
    author = data.get('author', existing[2])
    genre = data.get('genre', existing[3])
    year = data.get('year', existing[4])
    pages = data.get('pages', existing[5])
    isbn = data.get('isbn', existing[6])
    success = update_book(book_id, title, author, genre, year, pages, isbn)
    if not success:
        return jsonify({'error': 'Failed to update book'}), 500
    return jsonify({'message': 'Book updated successfully'}), 200

@admin_bp.route('/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    success = delete_book(book_id)
    if not success:
        return jsonify({'error': 'Failed to delete book'}), 500
    return jsonify({'message': 'Book deleted successfully'}), 200


@admin_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
def admin_borrow_book(book_id):
    data = request.get_json()
    user_id = data.get('user_id')
    borrow_date = data.get('borrow_date')
    due_date = data.get('due_date')
    if not all([user_id, borrow_date, due_date]):
        return jsonify({'error': 'Missing user_id, borrow_date, or due_date'}), 400
    success, message = borrow_book(book_id, user_id, borrow_date, due_date)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)

@admin_bp.route('/books/<int:book_id>/return', methods=['POST'])
def admin_return_book(book_id):
    return_date = request.get_json().get('return_date')
    if not return_date:
        return jsonify({'error': 'Missing return_date'}), 400
    success, message = return_book(book_id, return_date)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)

@admin_bp.route('/books/<int:book_id>/purchase', methods=['POST'])
def admin_purchase_book(book_id):
    data = request.get_json()
    user_id = data.get('user_id')
    purchase_date = data.get('purchase_date')
    price_paid = data.get('price_paid')
    if not all([user_id, purchase_date, price_paid]):
        return jsonify({'error': 'Missing user_id, purchase_date, or price_paid'}), 400
    success, message = purchase_book(book_id, user_id, purchase_date, price_paid)
    return (jsonify({'error': message}), 400) if not success else (jsonify({'message': message}), 200)