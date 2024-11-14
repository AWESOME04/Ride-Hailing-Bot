from config import db
from models.emergency_contact import EmergencyContact

class EmergencyContactService:
    @staticmethod
    def add_emergency_contact(user_hashed_id, contact_number):
        try:
            new_contact = EmergencyContact(user_hashed_id=user_hashed_id, contact_number=contact_number)
            db.session.add(new_contact)
            db.session.commit()
            return True, "Emergency contact saved successfully ."
        except Exception as e:
            return False, "There was an error saving your emergency contact ☹. Please try again."

    @staticmethod
    def get_emergency_contact(user_hashed_id):
        return EmergencyContact.query.filter_by(user_hashed_id=user_hashed_id).first()