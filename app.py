from flask import Flask, render_template
from routes.main_route import main_bp
from routes.user_routes import user_bp
from routes.admin_route import admin_bp  

app = Flask(__name__)
app.config['SECRET_KEY'] = "mahalpakitatalag123"

app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def landing_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)