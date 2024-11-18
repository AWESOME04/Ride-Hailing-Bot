from datetime import datetime
from models.ride import Ride
from config import db

class RideSummaryService:
    def get_ride_summary(self, ride_id):
        ride = Ride.query.get(ride_id)
        if not ride:
            return None
        return ride.get_summary()

    def complete_ride(self, ride_id, actual_fare):
        ride = Ride.query.get(ride_id)
        if ride:
            ride.status = 'COMPLETED'
            ride.end_time = datetime.utcnow()
            ride.actual_fare = actual_fare
            db.session.commit()
            return True
        return False

    def rate_ride(self, ride_id, rating, review):
        ride = Ride.query.get(ride_id)
        if ride and 1 <= rating <= 5:
            ride.rating = rating
            ride.review = review
            db.session.commit()
            return True
        return False

    def get_user_ride_history(self, user_hashed_id):
        rides = Ride.query.filter_by(
            user_hashed_id=user_hashed_id
        ).order_by(Ride.created_at.desc()).all()
        
        return [ride.get_summary() for ride in rides]
