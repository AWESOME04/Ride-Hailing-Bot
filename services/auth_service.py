from config import db
from models.user import User

class AuthService:
    @staticmethod
    def signup_user(name, role, whatsapp_number):
        try:
            new_user = User(name=name, role=role, whatsapp_number=whatsapp_number)
            db.session.add(new_user)
            db.session.commit()
            return True, "Thanks for signing up! You're now logged in. To ensure your safety, please provide an emergency contact (e.g., 0570081720."
        except Exception as e:
            return False, "There was an error with your signup ☹. Please format as 'Full Name, role'."

    @staticmethod
    def get_user_by_number(whatsapp_number):
        return User.query.filter_by(whatsapp_number=whatsapp_number).first()