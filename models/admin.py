from models import db

class Admin(db.Model):
    __tablename__ = 'admin'
    __table_args__ = {'extend_existing': True}  # ✅ מונע שגיאה אם הטבלה כבר קיימת

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
