// Helper to make authenticated fetch
async function apiFetch(url, options = {}) {
    options.credentials = 'include';
    options.headers = {
        Accept: 'application/json',
        ...(options.headers || {}),
    };
    const response = await fetch(url, options);
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || `HTTP ${response.status}`);
    }
    return response.json();
}

// Check session and get user profile
async function checkSession() {
    try {
        const user = await apiFetch('/user/profile');
        return { loggedIn: true, user };
    } catch (err) {
        return { loggedIn: false, user: null };
    }
}

// Render navigation based on auth (admin tools available to any signed-in user)
function renderNav(user) {
    const navDiv = document.getElementById('navLinks');
    if (!navDiv) return;
    if (!user) {
        navDiv.innerHTML = `
            <a href="#" onclick="showView('login'); return false;">Sign in</a>
            <a href="#" onclick="showView('register'); return false;">Register</a>
        `;
    } else {
        navDiv.innerHTML = `
            <a href="#" onclick="showView('dashboard'); return false;">Dashboard</a>
            <a href="#" onclick="showView('books'); return false;">Books</a>
            <a href="#" onclick="showView('profile'); return false;">Profile</a>
            <a href="#" onclick="showView('admin'); return false;">Manage library</a>
            <a href="#" onclick="logout(); return false;">Sign out</a>
        `;
    }
}

// Show a specific view
async function showView(viewName, params = {}) {
    const session = await checkSession();
    const user = session.user;
    renderNav(user);

    const viewContainer = document.getElementById('view');
    switch (viewName) {
        case 'login':
            viewContainer.innerHTML = renderLoginForm();
            break;
        case 'register':
            viewContainer.innerHTML = renderRegisterForm();
            break;
        case 'dashboard':
            if (!user) { showView('login'); return; }
            viewContainer.innerHTML = await renderUserDashboard(user);
            break;
        case 'profile':
            if (!user) { showView('login'); return; }
            viewContainer.innerHTML = await renderProfile(user);
            break;
        case 'books':
            viewContainer.innerHTML = await renderBookList();
            break;
        case 'bookDetail':
            viewContainer.innerHTML = await renderBookDetail(params.bookId);
            break;
        case 'borrowed':
            viewContainer.innerHTML = await renderBorrowedBooks();
            break;
        case 'history':
            viewContainer.innerHTML = await renderBorrowHistory();
            break;
        case 'purchases':
            viewContainer.innerHTML = await renderPurchaseHistory();
            break;
        case 'admin':
            if (!user) { showView('login'); return; }
            viewContainer.innerHTML = await renderAdminDashboard();
            break;
        default:
            viewContainer.innerHTML = '<h1>Welcome to S.H.E.L.F.</h1><p>System Hub For Efficient Library Functions — please sign in or register.</p>';
    }
}

// ----- RENDER FUNCTIONS -----
function renderLoginForm() {
    return `
        <div class="card">
            <h2>Login</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    `;
}

function renderRegisterForm() {
    return `
        <div class="card">
            <h2>Register</h2>
            <form id="registerForm">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Register</button>
            </form>
        </div>
    `;
}

async function renderUserDashboard(user) {
    let borrowedCount = 0, historyCount = 0, purchasesCount = 0;
    try {
        const borrowed = await apiFetch('/user/borrowed');
        borrowedCount = borrowed.length;
    } catch (e) {}
    try {
        const history = await apiFetch('/user/history');
        historyCount = history.length;
    } catch (e) {}
    try {
        const purchases = await apiFetch('/user/purchases');
        purchasesCount = purchases.length;
    } catch (e) {}
    return `
        <div class="card">
            <h2>Welcome, ${user.username}</h2>
            <div class="flex">
                <div class="card" style="flex:1">
                    <h3>Currently Borrowed</h3>
                    <p>${borrowedCount} books</p>
                    <button class="btn-outline" onclick="showView('borrowed')">View</button>
                </div>
                <div class="card" style="flex:1">
                    <h3>Borrowing History</h3>
                    <p>${historyCount} records</p>
                    <button class="btn-outline" onclick="showView('history')">View</button>
                </div>
                <div class="card" style="flex:1">
                    <h3>Purchases</h3>
                    <p>${purchasesCount} books</p>
                    <button class="btn-outline" onclick="showView('purchases')">View</button>
                </div>
            </div>
        </div>
    `;
}

async function renderProfile(user) {
    return `
        <div class="card">
            <h2>Edit Profile</h2>
            <form id="profileForm">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" value="${user.username}">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value="${user.email}">
                </div>
                <div class="form-group">
                    <label>New Password (leave blank to keep current)</label>
                    <input type="password" name="password">
                </div>
                <button type="submit">Update</button>
            </form>
        </div>
    `;
}

async function renderBookList() {
    const urlParams = new URLSearchParams(window.location.search);
    const sortBy = urlParams.get('sort_by') || 'title';
    const order = urlParams.get('order') || 'ASC';
    const books = await apiFetch(`/user/books?sort_by=${sortBy}&order=${order}`);
    return `
        <div class="card">
            <h2>Books</h2>
            <div class="flex" style="justify-content: space-between;">
                <div>
                    <label>Sort by: </label>
                    <select id="sortBy">
                        <option value="title" ${sortBy === 'title' ? 'selected' : ''}>Title</option>
                        <option value="author" ${sortBy === 'author' ? 'selected' : ''}>Author</option>
                        <option value="genre" ${sortBy === 'genre' ? 'selected' : ''}>Genre</option>
                        <option value="year" ${sortBy === 'year' ? 'selected' : ''}>Year</option>
                        <option value="pages" ${sortBy === 'pages' ? 'selected' : ''}>Pages</option>
                        <option value="isbn" ${sortBy === 'isbn' ? 'selected' : ''}>ISBN</option>
                    </select>
                    <select id="order">
                        <option value="ASC" ${order === 'ASC' ? 'selected' : ''}>Ascending</option>
                        <option value="DESC" ${order === 'DESC' ? 'selected' : ''}>Descending</option>
                    </select>
                    <button onclick="applySort()">Apply</button>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Title</th><th>Author</th><th>Genre</th><th>Year</th><th>Pages</th><th>ISBN</th><th>Action</th></tr>
                </thead>
                <tbody>
                    ${books.map(book => `
                        <tr>
                            <td>${book.book_id}</td>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.genre}</td>
                            <td>${book.year}</td>
                            <td>${book.pages}</td>
                            <td>${book.isbn}</td>
                            <td><button onclick="showView('bookDetail', {bookId: ${book.book_id}})">Details</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderBookDetail(bookId) {
    const book = await apiFetch(`/user/books/${bookId}`);
    // Assuming book tuple: (id, title, author, genre, year, pages, isbn)
    return `
        <div class="card">
            <h2>${book.title}</h2>
            <p><strong>Author:</strong> ${book.author}</p>
            <p><strong>Genre:</strong> ${book.genre}</p>
            <p><strong>Year:</strong> ${book.year}</p>
            <p><strong>Pages:</strong> ${book.pages}</p>
            <p><strong>ISBN:</strong> ${book.isbn}</p>
            <div class="flex">
                <button onclick="showBorrowForm(${bookId})">Borrow</button>
                <button onclick="showPurchaseForm(${bookId})">Purchase</button>
            </div>
            <div id="borrowForm${bookId}" class="hidden">
                <h3>Borrow Book</h3>
                <form onsubmit="borrowBook(${bookId}); return false;">
                    <div class="form-group"><label>Borrow Date (YYYY-MM-DD)</label><input type="date" name="borrow_date" required></div>
                    <div class="form-group"><label>Due Date (YYYY-MM-DD)</label><input type="date" name="due_date" required></div>
                    <button type="submit">Submit</button>
                </form>
            </div>
            <div id="purchaseForm${bookId}" class="hidden">
                <h3>Purchase Book</h3>
                <form onsubmit="purchaseBook(${bookId}); return false;">
                    <div class="form-group"><label>Purchase Date (YYYY-MM-DD)</label><input type="date" name="purchase_date" required></div>
                    <div class="form-group"><label>Price Paid</label><input type="number" step="0.01" name="price_paid" required></div>
                    <button type="submit">Submit</button>
                </form>
            </div>
        </div>
    `;
}

async function renderBorrowedBooks() {
    const borrowed = await apiFetch('/user/borrowed');
    if (!borrowed.length) return '<div class="card"><p>No books currently borrowed.</p></div>';
    return `
        <div class="card">
            <h2>Currently Borrowed Books</h2>
            <table>
                <thead><tr><th>Title</th><th>Author</th><th>Borrow Date</th><th>Due Date</th><th>Return</th></tr></thead>
                <tbody>
                    ${borrowed.map(book => `
                        <tr>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.borrow_date}</td>
                            <td>${book.due_date}</td>
                            <td><button onclick="returnBook(${book.book_id})">Return</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderBorrowHistory() {
    const history = await apiFetch('/user/history');
    if (!history.length) return '<div class="card"><p>No borrowing history.</p></div>';
    return `
        <div class="card">
            <h2>Borrowing History</h2>
            <table>
                <thead><tr><th>Title</th><th>Author</th><th>Borrow Date</th><th>Due Date</th><th>Return Date</th></tr></thead>
                <tbody>
                    ${history.map(book => `
                        <tr>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.borrow_date}</td>
                            <td>${book.due_date}</td>
                            <td>${book.return_date || 'Not returned'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderPurchaseHistory() {
    const purchases = await apiFetch('/user/purchases');
    if (!purchases.length) return '<div class="card"><p>No purchases.</p></div>';
    return `
        <div class="card">
            <h2>Purchased Books</h2>
            <table>
                <thead><tr><th>Title</th><th>Author</th><th>Purchase Date</th><th>Price Paid</th></tr></thead>
                <tbody>
                    ${purchases.map(book => `
                        <tr>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.purchase_date}</td>
                            <td>$${book.price_paid}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function renderAdminDashboard() {
    let stats = { total_users: 0, total_books: 0, active_borrows: 0 };
    let users = [];
    let books = [];
    try {
        stats = await apiFetch('/admin/dashboard');
        users = await apiFetch('/admin/users');
        books = await apiFetch('/admin/books');
    } catch (e) {
        return `<div class="card"><h2>Manage library</h2><p>Could not load admin data. Sign in on the main site first, then open this view again. (${e.message})</p></div>`;
    }
    return `
        <div class="card">
            <h2>Manage library</h2>
            <div class="flex">
                <div class="card">Total Users: ${stats.total_users}</div>
                <div class="card">Total Books: ${stats.total_books}</div>
                <div class="card">Active Borrows: ${stats.active_borrows}</div>
            </div>
            <h3>User Management</h3>
            <button onclick="showCreateUserForm()">Add User</button>
            <div id="createUserForm" class="hidden">
                <form onsubmit="createUser(); return false;">
                    <div class="form-group"><label>Username</label><input type="text" id="newUsername" required></div>
                    <div class="form-group"><label>Email</label><input type="email" id="newEmail" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="newPassword" required></div>
                    <button type="submit">Create</button>
                </form>
            </div>
            <table>
                <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Joined</th><th>Actions</th></tr></thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.user_id}</td>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.created_at || '—'}</td>
                            <td>
                                <button onclick="editUser(${user.user_id})">Edit</button>
                                <button onclick="deleteUser(${user.user_id})">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            <h3>Book Management</h3>
            <button onclick="showCreateBookForm()">Add Book</button>
            <div id="createBookForm" class="hidden">
                <form onsubmit="createBook(); return false;">
                    <div class="form-group"><label>Title</label><input type="text" id="newTitle" required></div>
                    <div class="form-group"><label>Author</label><input type="text" id="newAuthor" required></div>
                    <div class="form-group"><label>Genre</label><input type="text" id="newGenre"></div>
                    <div class="form-group"><label>Year</label><input type="number" id="newYear"></div>
                    <div class="form-group"><label>Pages</label><input type="number" id="newPages"></div>
                    <div class="form-group"><label>ISBN</label><input type="text" id="newIsbn" required></div>
                    <button type="submit">Create</button>
                </form>
            </div>
            <table>
                <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Genre</th><th>Year</th><th>Pages</th><th>ISBN</th><th>Actions</th></tr></thead>
                <tbody>
                    ${books.map(book => `
                        <tr>
                            <td>${book.book_id}</td>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.genre}</td>
                            <td>${book.year}</td>
                            <td>${book.pages}</td>
                            <td>${book.isbn}</td>
                            <td>
                                <button onclick="editBook(${book.book_id})">Edit</button>
                                <button onclick="deleteBook(${book.book_id})">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ----- EVENT HANDLERS (must be globally available) -----
window.showView = showView;

window.applySort = function() {
    const sortBy = document.getElementById('sortBy').value;
    const order = document.getElementById('order').value;
    window.history.pushState({}, '', `?sort_by=${sortBy}&order=${order}`);
    showView('books');
};

window.showBorrowForm = function(bookId) {
    document.getElementById(`borrowForm${bookId}`).classList.toggle('hidden');
};

window.showPurchaseForm = function(bookId) {
    document.getElementById(`purchaseForm${bookId}`).classList.toggle('hidden');
};

window.borrowBook = async function(bookId) {
    const form = document.querySelector(`#borrowForm${bookId} form`);
    const borrow_date = form.borrow_date.value;
    const due_date = form.due_date.value;
    try {
        await apiFetch(`/user/books/${bookId}/borrow`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({borrow_date, due_date})
        });
        alert('Book borrowed successfully!');
        showView('bookDetail', {bookId});
    } catch (err) {
        alert('Error: ' + err.message);
    }
};

window.purchaseBook = async function(bookId) {
    const form = document.querySelector(`#purchaseForm${bookId} form`);
    const purchase_date = form.purchase_date.value;
    const price_paid = form.price_paid.value;
    try {
        await apiFetch(`/user/books/${bookId}/purchase`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({purchase_date, price_paid})
        });
        alert('Book purchased successfully!');
        showView('bookDetail', {bookId});
    } catch (err) {
        alert('Error: ' + err.message);
    }
};

window.returnBook = async function(bookId) {
    const return_date = new Date().toISOString().slice(0,10);
    try {
        await apiFetch(`/user/books/${bookId}/return`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({return_date})
        });
        alert('Book returned successfully!');
        showView('borrowed');
    } catch (err) {
        alert('Error: ' + err.message);
    }
};

window.logout = async function() {
    try {
        await apiFetch('/logout', {method: 'POST'});
        showView('login');
    } catch (err) {
        alert('Logout failed: ' + err.message);
    }
};

// Form submissions (attach after rendering)
document.addEventListener('submit', async (e) => {
    if (e.target.id === 'loginForm') {
        e.preventDefault();
        const form = e.target;
        const email = form.email.value;
        const password = form.password.value;
        try {
            await apiFetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            showView('dashboard');
        } catch (err) {
            alert('Login failed: ' + err.message);
        }
    } else if (e.target.id === 'registerForm') {
        e.preventDefault();
        const form = e.target;
        const username = form.username.value;
        const email = form.email.value;
        const password = form.password.value;
        try {
            await apiFetch('/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, email, password})
            });
            alert('Registration successful! Please login.');
            showView('login');
        } catch (err) {
            alert('Registration failed: ' + err.message);
        }
    } else if (e.target.id === 'profileForm') {
        e.preventDefault();
        const form = e.target;
        const username = form.username.value;
        const email = form.email.value;
        const password = form.password.value;
        try {
            await apiFetch('/user/profile', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, email, password})
            });
            alert('Profile updated!');
            showView('dashboard');
        } catch (err) {
            alert('Update failed: ' + err.message);
        }
    }
});

// Admin functions
window.showCreateUserForm = () => {
    document.getElementById('createUserForm').classList.toggle('hidden');
};
window.createUser = async () => {
    const username = document.getElementById('newUsername').value;
    const email = document.getElementById('newEmail').value;
    const password = document.getElementById('newPassword').value;
    try {
        await apiFetch('/admin/users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, email, password})
        });
        alert('User created');
        showView('admin');
    } catch (err) {
        alert('Error: ' + err.message);
    }
};
window.editUser = (id) => {
    const newUsername = prompt('New username:');
    const newEmail = prompt('New email:');
    const newPassword = prompt('New password (leave blank to keep):');
    const data = {};
    if (newUsername) data.username = newUsername;
    if (newEmail) data.email = newEmail;
    if (newPassword) data.password = newPassword;
    if (Object.keys(data).length === 0) return;
    apiFetch(`/admin/users/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(() => {
        alert('User updated');
        showView('admin');
    }).catch(err => alert('Error: ' + err.message));
};
window.deleteUser = async (id) => {
    if (!confirm('Delete this user?')) return;
    try {
        await apiFetch(`/admin/users/${id}`, {method: 'DELETE'});
        alert('User deleted');
        showView('admin');
    } catch (err) {
        alert('Error: ' + err.message);
    }
};
window.showCreateBookForm = () => {
    document.getElementById('createBookForm').classList.toggle('hidden');
};
window.createBook = async () => {
    const title = document.getElementById('newTitle').value;
    const author = document.getElementById('newAuthor').value;
    const genre = document.getElementById('newGenre').value;
    const year = document.getElementById('newYear').value;
    const pages = document.getElementById('newPages').value;
    const isbn = document.getElementById('newIsbn').value;
    try {
        await apiFetch('/admin/books', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title, author, genre, year, pages, isbn})
        });
        alert('Book created');
        showView('admin');
    } catch (err) {
        alert('Error: ' + err.message);
    }
};
window.editBook = async (id) => {
    // Fetch current data first
    const book = await apiFetch(`/admin/books/${id}`);
    const newTitle = prompt('Title:', book.title);
    const newAuthor = prompt('Author:', book.author);
    const newGenre = prompt('Genre:', book.genre);
    const newYear = prompt('Year:', book.year);
    const newPages = prompt('Pages:', book.pages);
    const newIsbn = prompt('ISBN:', book.isbn);
    const data = {};
    if (newTitle) data.title = newTitle;
    if (newAuthor) data.author = newAuthor;
    if (newGenre) data.genre = newGenre;
    if (newYear) data.year = newYear;
    if (newPages) data.pages = newPages;
    if (newIsbn) data.isbn = newIsbn;
    if (Object.keys(data).length === 0) return;
    await apiFetch(`/admin/books/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    alert('Book updated');
    showView('admin');
};
window.deleteBook = async (id) => {
    if (!confirm('Delete this book?')) return;
    try {
        await apiFetch(`/admin/books/${id}`, {method: 'DELETE'});
        alert('Book deleted');
        showView('admin');
    } catch (err) {
        alert('Error: ' + err.message);
    }
};

// Initial view (check login)
checkSession().then(session => {
    if (session.loggedIn) {
        showView('dashboard');
    } else {
        showView('login');
    }
});