from twilio.twiml.messaging_response import MessagingResponse
from services.auth_service import AuthService
from services.emergency_contact_service import EmergencyContactService
from services.profile_service import ProfileService

class MessageHandler:
    def __init__(self):
        self.auth_service = AuthService()
        self.emergency_contact_service = EmergencyContactService()
        self.profile_service = ProfileService()
        self.user_states = {}

    def handle_message(self, incoming_msg, from_number):
        resp = MessagingResponse()
        user = self.auth_service.get_user_by_number(from_number)

        if user:
            return self._handle_registered_user(user, incoming_msg, from_number, resp)
        else:
            return self._handle_unregistered_user(incoming_msg, from_number, resp)

    def _handle_registered_user(self, user, incoming_msg, from_number, resp):
        user_state = self.user_states.get(from_number, {})
        
        if user_state.get('editing'):
            return self._handle_edit_flow(user, incoming_msg, from_number, resp)
        
        if incoming_msg.lower() == 'help':
            resp.message("Here are the available commands:\n"
                        "- start: Begin a new trip\n"
                        "- stop: To stop your current trip\n"
                        "- edit: To edit your profile\n"
                        "- status: View your current profile")
        elif incoming_msg.lower() == 'edit':
            self.user_states[from_number] = {'editing': True}
            resp.message("What would you like to edit?\n"
                        "1. Name\n"
                        "2. Role\n"
                        "3. Emergency Contact\n"
                        "Reply with the number of your choice or 'cancel' to exit.")
        elif incoming_msg.lower() == 'status':
            emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)
            contact_number = emergency_contact.contact_number if emergency_contact else "Not set"
            resp.message(f"Your Profile:\n"
                        f"Name: {user.name}\n"
                        f"Role: {user.role}\n"
                        f"Emergency Contact: {contact_number}")
        else:
            emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)
            
            if not emergency_contact:
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
            try:
                name, role = [i.strip() for i in incoming_msg.split(',', 1)]
                if name and role:
                    success, message = self.auth_service.signup_user(name, role, from_number)
                    resp.message(message)
                else:
                    resp.message("There was an error with your signup. Please make sure to include both your name and role separated by a comma.")
            except Exception as e:
                resp.message("There was an error with your signup ☹. Please format as 'Full Name, role'.")
        else:
            resp.message("Welcome! Please type 'sign up' to create an account.")
            
        return str(resp)

    def _handle_edit_flow(self, user, incoming_msg, from_number, resp):
        user_state = self.user_states.get(from_number, {})
        
        if incoming_msg.lower() == 'cancel':
            self.user_states.pop(from_number, None)
            resp.message("Edit cancelled. Type 'help' to see available commands.")
            return str(resp)

        if 'waiting_for' not in user_state:
            if incoming_msg in ['1', '2', '3']:
                choice = int(incoming_msg)
                if choice == 1:
                    self.user_states[from_number]['waiting_for'] = 'name'
                    resp.message("Please enter your new name:")
                elif choice == 2:
                    self.user_states[from_number]['waiting_for'] = 'role'
                    resp.message("Please enter your new role:")
                elif choice == 3:
                    self.user_states[from_number]['waiting_for'] = 'emergency_contact'
                    resp.message("Please enter your new emergency contact number (10 digits):")
            else:
                resp.message("Please select a valid option (1-3) or type 'cancel' to exit:")
        else:
            waiting_for = user_state['waiting_for']
            success = False
            message = ""

            if waiting_for == 'name':
                success, message = self.profile_service.update_name(user, incoming_msg)
            elif waiting_for == 'role':
                success, message = self.profile_service.update_role(user, incoming_msg)
            elif waiting_for == 'emergency_contact':
                if incoming_msg.isdigit() and len(incoming_msg) == 10:
                    success, message = self.profile_service.update_emergency_contact(user.hashed_id, incoming_msg)
                else:
                    message = "Please enter a valid 10-digit phone number or type 'cancel' to exit."
                    success = False

            if success:
                self.user_states.pop(from_number, None)
                message += "\n\nEdit complete. Type 'status' to view your profile or 'edit' to make more changes."
            
            resp.message(message)

        return str(resp)