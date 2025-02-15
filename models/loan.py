from models import db
from datetime import datetime


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # קשר למשחק
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    # קשר ללקוח
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    # תאריך ההשכרה
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
