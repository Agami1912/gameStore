from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import datetime

# אתחול Flask והגדרות בסיס נתונים
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # שנה למפתח סודי אמיתי
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# אתחול רכיבי Flask
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)  # תומך בקוקיז עבור session


# 📌 מודל מנהלים (Admin)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# 📌 מודל משחקים (Game)
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    loan_status = db.Column(db.Boolean, default=False)


# 📌 מודל לקוחות (Customer)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    loans = db.relationship('Loan', backref='customer', lazy=True)


# 📌 מודל השאלות (Loan)
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# אתחול מסד הנתונים
with app.app_context():
    db.create_all()


# 📌 הרשמת מנהל (Sign Up)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_admin = Admin(username=data['username'], password=hashed_password)

    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Admin registered successfully"}), 201
    except:
        return jsonify({"error": "Username already exists"}), 400


# 📌 התחברות מנהל (Login)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    admin = Admin.query.filter_by(username=data['username']).first()

    if admin and bcrypt.check_password_hash(admin.password, data['password']):
        session['admin_id'] = admin.id  # שמירת session
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# 📌 יציאה ממערכת (Logout)
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_id', None)
    return jsonify({"message": "Logged out successfully"}), 200


# 📌 קבלת רשימת המשחקים
@app.route('/games', methods=['GET'])
def get_games():
    games = Game.query.all()
    return jsonify([{
        "id": game.id, "title": game.title, "genre": game.genre,
        "price": game.price, "quantity": game.quantity, "loan_status": game.loan_status
    } for game in games])


# 📌 הוספת משחק חדש
@app.route('/games', methods=['POST'])
def add_game():
    data = request.get_json()
    new_game = Game(title=data['title'], genre=data['genre'],
                    price=data['price'], quantity=data['quantity'])

    db.session.add(new_game)
    db.session.commit()
    return jsonify({"message": "Game added successfully"}), 201


# 📌 מחיקת משחק
@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    db.session.delete(game)
    db.session.commit()
    return jsonify({"message": "Game deleted successfully"}), 200


# 📌 רישום לקוח חדש
@app.route('/customers', methods=['POST'])
def register_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])

    try:
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer registered successfully"}), 201
    except:
        return jsonify({"error": "Email already exists"}), 400


# 📌 השאלת משחק ללקוח
@app.route('/loan', methods=['POST'])
def loan_game():
    data = request.get_json()
    game = Game.query.get(data['game_id'])
    customer = Customer.query.get(data['customer_id'])

    if not game or not customer:
        return jsonify({"error": "Game or Customer not found"}), 404

    if game.loan_status:
        return jsonify({"error": "Game is already loaned"}), 400

    new_loan = Loan(game_id=game.id, customer_id=customer.id)
    game.loan_status = True  # עדכון סטטוס השאלה

    db.session.add(new_loan)
    db.session.commit()
    return jsonify({"message": "Game loaned successfully"}), 201


# 📌 קבלת כל המשחקים המושאלים כרגע
@app.route('/loaned-games', methods=['GET'])
def get_loaned_games():
    loans = Loan.query.all()
    return jsonify([{
        "game_id": loan.game_id, "customer_id": loan.customer_id,
        "loan_date": loan.loan_date.strftime("%Y-%m-%d %H:%M:%S")
    } for loan in loans])


if __name__ == '__main__':
    app.run(debug=True)
