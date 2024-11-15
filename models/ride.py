from config import db
from datetime import datetime

class Ride(db.Model):
    __tablename__ = 'rides'
    id = db.Column(db.Integer, primary_key=True)
    user_hashed_id = db.Column(db.String(128), db.ForeignKey('users.hashed_id'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='REQUESTED')
    ride_type = db.Column(db.String(50), nullable=False)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    car_model = db.Column(db.String(100))
    car_number = db.Column(db.String(20))
    estimated_fare = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)