from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# 🔧 קביעת הגדרות האפליקציה
app.config['SECRET_KEY'] = 'your_secret_key'  # יש להחליף במפתח סודי אמיתי
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

#  אתחול הכלים
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

#  טבלת מנהלים (Admins)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

#  טבלת משחקים (Games)
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    loaned_to = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)

#  טבלת לקוחות (Customers)
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    loans = db.relationship('Game', backref='customer', lazy=True)

# אתחול בסיס הנתונים
with app.app_context():
    db.create_all()

#  רישום מנהל (Sign Up)
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

# התחברות מנהל (Login)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    admin = Admin.query.filter_by(username=data['username']).first()

    if admin and bcrypt.check_password_hash(admin.password, data['password']):
        session['admin_id'] = admin.id
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

#  התנתקות (Logout)
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

#  הצגת כל המשחקים
@app.route('/games', methods=['GET'])
def get_games():
    games = Game.query.all()
    return jsonify([{"id": g.id, "title": g.title, "genre": g.genre, "price": g.price, "quantity": g.quantity, "loaned_to": g.loaned_to} for g in games])

# הוספת משחק חדש
@app.route('/games', methods=['POST'])
def add_game():
    data = request.get_json()
    new_game = Game(title=data['title'], genre=data['genre'], price=data['price'], quantity=data['quantity'])
    db.session.add(new_game)
    db.session.commit()
    return jsonify({"message": "Game added successfully"}), 201

#  מחיקת משחק
@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    db.session.delete(game)
    db.session.commit()
    return jsonify({"message": "Game deleted successfully"}), 200

#  רישום לקוח חדש
@app.route('/customers', methods=['POST'])
def register_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer registered successfully"}), 201

#  השאלת משחק ללקוח
@app.route('/loans', methods=['POST'])
def loan_game():
    data = request.get_json()
    game = Game.query.get(data['game_id'])
    customer = Customer.query.get(data['customer_id'])

    if not game or not customer:
        return jsonify({"error": "Invalid game or customer"}), 400

    if game.loaned_to:
        return jsonify({"error": "Game is already loaned out"}), 400

    game.loaned_to = customer.id
    db.session.commit()
    return jsonify({"message": "Game loaned successfully"}), 200

#  הצגת כל ההשאלות
@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Game.query.filter(Game.loaned_to.isnot(None)).all()
    return jsonify([{"game_id": g.id, "title": g.title, "customer_id": g.loaned_to} for g in loans])

if __name__ == '__main__':
    app.run(debug=True)
