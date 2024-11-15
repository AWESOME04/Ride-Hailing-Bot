from twilio.twiml.messaging_response import MessagingResponse
from services.auth_service import AuthService
from services.emergency_contact_service import EmergencyContactService
from services.profile_service import ProfileService
from services.ride_service import RideService

class MessageHandler:
    def __init__(self):
        self.auth_service = AuthService()
        self.emergency_contact_service = EmergencyContactService()
        self.profile_service = ProfileService()
        self.ride_service = RideService()
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
            
        if user_state.get('booking_ride'):
            return self._handle_ride_booking_flow(user, incoming_msg, from_number, resp)

        active_ride = self.ride_service.get_active_ride(user.hashed_id)
        if active_ride and incoming_msg.lower() not in ['cancel', 'help', 'status', 'end']:
            return self._handle_active_ride(active_ride, incoming_msg, resp)

        if incoming_msg.lower() == 'help':
            resp.message("Here are the available commands:\n"
                        "- start: Begin a new trip\n"
                        "- end: Stop your current trip\n"
                        "- edit: Edit your profile\n"
                        "- status: View your profile/ride status\n"
                        "- cancel: Cancel current action")
        elif incoming_msg.lower() == 'edit':
            self.user_states[from_number] = {'editing': True}
            resp.message("What would you like to edit?\n"
                        "1. Name\n"
                        "2. Role\n"
                        "3. Emergency Contact\n"
                        "Reply with the number of your choice or 'cancel' to exit.")
        elif incoming_msg.lower() == 'status':
            if active_ride:
                return self._handle_active_ride(active_ride, 'status', resp)
            else:
                emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)
                contact_number = emergency_contact.contact_number if emergency_contact else "Not set"
                resp.message(f"Your Profile:\n"
                            f"Name: {user.name}\n"
                            f"Role: {user.role}\n"
                            f"Emergency Contact: {contact_number}")
        elif incoming_msg.lower() == 'start':
            if active_ride:
                resp.message("You already have an active ride. Type 'status' to check its status or 'end' to cancel it.")
            else:
                emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)
                if not emergency_contact:
                    resp.message("To ensure your safety, please provide an emergency contact 📱 (e.g., 0570081720)")
                else:
                    self.user_states[from_number] = {
                        'booking_ride': True,
                        'step': 'pickup'
                    }
                    resp.message("Please share your pickup location 📍")
        elif incoming_msg.lower() == 'end':
            if active_ride:
                return self._handle_active_ride(active_ride, 'end', resp)
            else:
                resp.message("You don't have any active rides. Type 'start' to begin a new trip.")
        else:
            emergency_contact = self.emergency_contact_service.get_emergency_contact(user.hashed_id)
            if not emergency_contact:
                if incoming_msg.isdigit() and len(incoming_msg) == 10:
                    success, message = self.emergency_contact_service.add_emergency_contact(user.hashed_id, incoming_msg)
                    resp.message(message)
                else:
                    resp.message("To ensure your safety, please provide an emergency contact 📱 (e.g., 0570081720)")
            else:
                resp.message("Welcome back! 😁 You're already logged in. Type 'start' to begin a new trip or 'help' to see available commands.")

        return str(resp)

    def _handle_ride_booking_flow(self, user, incoming_msg, from_number, resp):
        user_state = self.user_states[from_number]
        
        if incoming_msg.lower() == 'cancel':
            self.user_states.pop(from_number, None)
            resp.message("Booking cancelled. Type 'start' to begin a new booking.")
            return str(resp)

        step = user_state.get('step')
        
        if step == 'pickup':
            user_state['pickup'] = incoming_msg
            user_state['step'] = 'destination'
            resp.message("Great! Now please share your destination location 📍")
            
        elif step == 'destination':
            user_state['destination'] = incoming_msg
            user_state['step'] = 'ride_type'
            resp.message("Please select your ride type:\n"
                        "1. Standard (Base: GH₵10, GH₵1.5/km)\n"
                        "2. Premium (Base: GH₵15, GH₵2.0/km)\n"
                        "3. XL (Base: GH₵20, GH₵2.5/km)")
            
        elif step == 'ride_type':
            if incoming_msg not in ['1', '2', '3']:
                resp.message("Please select a valid ride type (1-3) or 'cancel' to exit")
                return str(resp)

            success, ride = self.ride_service.create_ride(
                user.hashed_id,
                user_state['pickup'],
                user_state['destination'],
                incoming_msg
            )

            if success:
                success, matched_ride = self.ride_service.match_driver(ride)
                if success:
                    est_time = self.ride_service.get_estimated_arrival_time()
                    self.user_states.pop(from_number, None)
                    resp.message(f"🚗 Ride Confirmed!\n\n"
                               f"Driver: {matched_ride.driver_name}\n"
                               f"Phone: {matched_ride.driver_phone}\n"
                               f"Car: {matched_ride.car_model}\n"
                               f"Number: {matched_ride.car_number}\n\n"
                               f"Estimated arrival: {est_time} minutes\n"
                               f"Estimated fare: GH₵{matched_ride.estimated_fare:.2f}")
                else:
                    resp.message("Sorry, we couldn't match you with a driver. Please try again later.")
            else:
                resp.message("Sorry, there was an error booking your ride. Please try again.")

        return str(resp)

    def _handle_active_ride(self, ride, incoming_msg, resp):
        if incoming_msg.lower() == 'end':
            if ride.status in ['REQUESTED', 'MATCHED']:
                success, _ = self.ride_service.update_ride_status(ride, 'CANCELLED')
                if success:
                    resp.message("Your ride has been cancelled.")
                else:
                    resp.message("Sorry, we couldn't cancel your ride. Please try again.")
            else:
                resp.message("Cannot cancel ride in progress. Please contact your driver.")
        elif incoming_msg.lower() == 'status':
            status_messages = {
                'REQUESTED': "Looking for a driver...",
                'MATCHED': f"Driver {ride.driver_name} is on the way!",
                'ARRIVED': "Your driver has arrived!",
                'IN_PROGRESS': "Your trip is in progress...",
                'COMPLETED': "Your trip has been completed.",
                'CANCELLED': "Your trip was cancelled."
            }
            est_time = self.ride_service.get_estimated_arrival_time() if ride.status == 'MATCHED' else None
            
            message = f"Ride Status: {status_messages[ride.status]}\n"
            if ride.status != 'REQUESTED':
                message += f"\nDriver: {ride.driver_name}\n"
                message += f"Car: {ride.car_model} ({ride.car_number})\n"
                if est_time:
                    message += f"Estimated arrival: {est_time} minutes\n"
            message += f"Estimated fare: GH₵{ride.estimated_fare:.2f}"
            
            resp.message(message)
        
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