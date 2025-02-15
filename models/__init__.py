from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.admin import Admin
from models.customer import Customer
from models.game import Game
from models.loan import Loan
