from models import db


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)

    # קשר בין לקוחות להשכרות - לקוח יכול לשכור מספר משחקים
    loans = db.relationship("Loan", backref="customer", lazy=True)
