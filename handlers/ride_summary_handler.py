from flask import jsonify
from services.ride_summary_service import RideSummaryService
from models.user import User

class RideSummaryHandler:
    def __init__(self):
        self.ride_summary_service = RideSummaryService()

    def get_ride_summary(self, ride_id, user_hashed_id):
        user = User.query.filter_by(hashed_id=user_hashed_id).first()
        if user and user.role == 'driver':
            return jsonify({"message": "Eyes on the road! 👀🚗"})

        summary = self.ride_summary_service.get_ride_summary(ride_id)
        if not summary:
            return jsonify({"error": "Ride not found"}), 404
        return jsonify(summary)

    def get_ride_history(self, user_hashed_id):
        user = User.query.filter_by(hashed_id=user_hashed_id).first()
        if user and user.role == 'driver':
            return jsonify({"message": "Eyes on the road! 👀🚗"})

        history = self.ride_summary_service.get_user_ride_history(user_hashed_id)
        return jsonify({"rides": history})
