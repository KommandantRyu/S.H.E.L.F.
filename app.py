import os

from flask import Flask, render_template
from json_util import ShelfJSONProvider
from routes.main_route import main_bp
from routes.user_routes import user_bp
from routes.admin_route import admin_bp

app = Flask(__name__)
app.json = ShelfJSONProvider(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-change-me-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def landing_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)