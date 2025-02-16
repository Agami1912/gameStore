from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=3)  # סשן יפוג לאחר 3 שעות

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)



class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    loan_status = db.Column(db.Boolean, default=False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)


# יצירת טבלאות אם אין
with app.app_context():
    db.create_all()


# דף הבית
@app.route('/')
def home():
    if 'admin_id' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('dashboard'))


# דף ניהול
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        flash("You must be logged in to access the dashboard", "warning")
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')


# דף התחברות
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


# API לרישום משתמש חדש
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data['username'] or not data['password']:
        return jsonify({"error": "Username and password are required"}), 400

    existing_admin = Admin.query.filter_by(username=data['username']).first()
    if existing_admin:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_admin = Admin(username=data['username'], password=hashed_password)

    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Admin registered successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error registering admin: {e}")
        return jsonify({"error": "Database error"}), 500


# API להתחברות
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data['username'] or not data['password']:
        return jsonify({"error": "Both username and password are required"}), 400

    admin = Admin.query.filter_by(username=data['username']).first()

    if admin and bcrypt.check_password_hash(admin.password, data['password']):
        session.permanent = True
        session['admin_id'] = admin.id
        session['username'] = admin.username
        app.logger.info(f"Login successful: {data['username']}")
        return jsonify({"message": "Login successful"}), 200

    app.logger.warning(f"Failed login attempt: {data['username']}")
    return jsonify({"error": "Invalid credentials"}), 401


# API להתנתקות
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return jsonify({"message": "Logged out successfully"}), 200
# API לניהול משחקים
@app.route('/api/games', methods=['GET', 'POST'])
def manage_games():
    print(f"Received {request.method} request at /api/games")  # הדפסת בקשה שהתקבלה
    if request.method == 'POST':
        data = request.get_json()
        print(f"Data received: {data}")  # בדיקה אם הנתונים מתקבלים

        if not data.get('title') or not data.get('genre') or not data.get('price') or not data.get('quantity'):
            return jsonify({"error": "All fields are required"}), 400

        new_game = Game(title=data['title'], genre=data['genre'], price=data['price'], quantity=data['quantity'])
        db.session.add(new_game)
        db.session.commit()
        print("Game added successfully!")  # לוודא שהתהליך הושלם
        return jsonify({"message": "Game added successfully"}), 201

    games = Game.query.all()
    return jsonify([{"id": game.id, "title": game.title, "genre": game.genre, "price": game.price,
                     "quantity": game.quantity, "loan_status": game.loan_status} for game in games])

# API להוספת לקוחות
@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.get_json()

    if not data.get('name') or not data.get('email') or not data.get('phone'):
        return jsonify({"error": "All fields are required"}), 400

    existing_customer = Customer.query.filter_by(email=data['email']).first()
    if existing_customer:
        return jsonify({"error": "Customer with this email already exists"}), 400

    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer registered successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True)
