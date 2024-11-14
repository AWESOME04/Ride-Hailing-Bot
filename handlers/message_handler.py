from twilio.twiml.messaging_response import MessagingResponse
from services.auth_service import AuthService
from services.emergency_contact_service import EmergencyContactService

class MessageHandler:
    def __init__(self):
        self.auth_service = AuthService()
        self.emergency_contact_service = EmergencyContactService()

    def handle_message(self, incoming_msg, from_number):
        resp = MessagingResponse()
        user = self.auth_service.get_user_by_number(from_number)

        if user:
            return self._handle_registered_user(user, incoming_msg, resp)
        else:
            return self._handle_unregistered_user(incoming_msg, from_number, resp)

    def _handle_registered_user(self, user, incoming_msg, resp):
        emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)

        if incoming_msg.lower() == 'help':
            resp.message("Here are the available commands:\n- start: Begin a new trip\n- stop: To stop your current trip\n- edit: To edit your user details")
        elif not emergency_contact:
            if incoming_msg.isdigit() and len(incoming_msg) == 10:
                success, message = self.emergency_contact_service.add_emergency_contact(user.hashed_id, incoming_msg)
                resp.message(message)
            else:
                resp.message("To ensure your safety, please provide an emergency contact 📱 (e.g., 0570081720.")
        else:
            resp.message("Welcome back! 😁 You're already logged in. Type start to begin a new trip. To see the various commands type help.")

        return str(resp)

    def _handle_unregistered_user(self, incoming_msg, from_number, resp):
        if incoming_msg.lower() == 'sign up':
            resp.message("Please reply with your full name and role (e.g., 'John Doe, passenger').")
        elif ',' in incoming_msg:
            name, role = [i.strip() for i in incoming_msg.split(',', 1)]
            if name and role:
                success, message = self.auth_service.signup_user(name, role, from_number)
                resp.message(message)
            else:
                resp.message("There was an error with your signup. Please make sure to include both your name and role separated by a comma.")

        return str(resp)