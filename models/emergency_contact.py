from config import db

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_hashed_id = db.Column(db.String(128), db.ForeignKey('users.hashed_id'), nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)

    def __init__(self, user_hashed_id, contact_number):
        self.user_hashed_id = user_hashed_id
        self.contact_number = contact_number