from config import db
import hashlib

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    whatsapp_number = db.Column(db.String(30), nullable=False, unique=True)
    hashed_id = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self, name, role, whatsapp_number):
        self.name = name
        self.role = role
        self.whatsapp_number = whatsapp_number
        self.hashed_id = hashlib.sha256(whatsapp_number.encode()).hexdigest()