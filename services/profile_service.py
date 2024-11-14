from config import db
from models.user import User
from models.emergency_contact import EmergencyContact

class ProfileService:
    @staticmethod
    def update_name(user, new_name):
        try:
            user.name = new_name
            db.session.commit()
            return True, f"Your name has been updated to: {new_name}"
        except Exception as e:
            db.session.rollback()
            return False, "Failed to update name. Please try again."

    @staticmethod
    def update_role(user, new_role):
        try:
            user.role = new_role
            db.session.commit()
            return True, f"Your role has been updated to: {new_role}"
        except Exception as e:
            db.session.rollback()
            return False, "Failed to update role. Please try again."

    @staticmethod
    def update_emergency_contact(user_hashed_id, new_contact):
        try:
            contact = EmergencyContact.query.filter_by(user_hashed_id=user_hashed_id).first()
            if contact:
                contact.contact_number = new_contact
            else:
                contact = EmergencyContact(user_hashed_id=user_hashed_id, contact_number=new_contact)
                db.session.add(contact)
            db.session.commit()
            return True, f"Emergency contact updated to: {new_contact}"
        except Exception as e:
            db.session.rollback()
            return False, "Failed to update emergency contact. Please try again."