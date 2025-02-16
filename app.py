from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(hours=3)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# Models
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
    loans = db.relationship('Loan', backref='game', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    loans = db.relationship('Loan', backref='customer', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
# יצירת טבלאות במסד הנתונים
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'admin_id' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        flash("You must be logged in to access the dashboard", "warning")
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

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



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return jsonify({"message": "Logged out successfully"}), 200
# API לניהול משחקים
# Game Management
@app.route('/api/games', methods=['GET', 'POST'])
def manage_games():
    if request.method == 'POST':
        data = request.get_json()
        new_game = Game(title=data['title'], genre=data['genre'], price=data['price'], quantity=data['quantity'])
        db.session.add(new_game)
        db.session.commit()
        return jsonify({"message": "Game added successfully"}), 201
    games = Game.query.all()
    return jsonify([{ "id": g.id, "title": g.title, "genre": g.genre, "price": g.price, "quantity": g.quantity } for g in games])

# Customer Management
@app.route('/api/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'POST':
        data = request.get_json()
        new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer added successfully"}), 201
    customers = Customer.query.all()
    return jsonify([{ "id": c.id, "name": c.name, "email": c.email, "phone": c.phone } for c in customers])

# Loan System
@app.route('/api/loans', methods=['GET', 'POST'])
def manage_loans():
    if request.method == 'GET':
        loans = Loan.query.all()
        return jsonify([{
            "id": loan.id,
            "game_id": loan.game_id,
            "customer_id": loan.customer_id,
            "loan_date": loan.loan_date.isoformat() if loan.loan_date else None,
            "return_date": loan.return_date.isoformat() if loan.return_date else None
        } for loan in loans])

    elif request.method == 'POST':
        data = request.get_json()

        # Check if game is available
        game = Game.query.get(data['game_id'])
        if not game or game.quantity <= 0:
            return jsonify({"error": "Game not available"}), 400

        # Create new loan
        new_loan = Loan(
            game_id=data['game_id'],
            customer_id=data['customer_id'],
            loan_date=datetime.utcnow()
        )

        # Decrease game quantity
        game.quantity -= 1

        db.session.add(new_loan)
        db.session.commit()
        return jsonify({"message": "Loan added successfully"}), 201

@app.route('/api/loans', methods=['GET', 'POST'])
@app.route('/api/loans/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    loan.return_date = datetime.utcnow()  # Set the return date when the game is returned

    # Update game quantity (assuming that the game is being returned to stock)
    game = Game.query.get(loan.game_id)
    if game:
        game.quantity += 1

    db.session.commit()
    return jsonify({"message": "Game returned successfully"})

if __name__ == '__main__':
    app.run(debug=True)
