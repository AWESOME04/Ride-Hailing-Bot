from flask import Blueprint, request, jsonify
from handlers.ride_summary_handler import RideSummaryHandler

ride_summary_bp = Blueprint('ride_summary', __name__)
handler = RideSummaryHandler()

@ride_summary_bp.route('/rides/<ride_id>/summary', methods=['GET'])
def get_ride_summary(ride_id):
    user_hashed_id = request.headers.get('X-User-Hashed-Id')
    if not user_hashed_id:
        return jsonify({"error": "User not authenticated"}), 401
    return handler.get_ride_summary(ride_id, user_hashed_id)

@ride_summary_bp.route('/rides/history', methods=['GET'])
def get_ride_history():
    user_hashed_id = request.headers.get('X-User-Hashed-Id')
    if not user_hashed_id:
        return jsonify({"error": "User not authenticated"}), 401
    return handler.get_ride_history(user_hashed_id)
