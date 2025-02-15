from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db  # ייבוא אובייקט ה- db שהגדרנו ב- __init__.py

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
