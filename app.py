from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    whatsapp_number = db.Column(db.String(30), nullable=False, unique=True)
    hashed_id = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self, name, role, whatsapp_number):
        self.name = name
        self.role = role
        self.whatsapp_number = whatsapp_number
        self.hashed_id = hashlib.sha256(whatsapp_number.encode()).hexdigest()

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_hashed_id = db.Column(db.String(128), db.ForeignKey('users.hashed_id'), nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)

    def __init__(self, user_hashed_id, contact_number):
        self.user_hashed_id = user_hashed_id
        self.contact_number = contact_number

@app.route('/')
def home():
    return "Hello, this is your WhatsApp bot!"

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '').strip()

    user = User.query.filter_by(whatsapp_number=from_number).first()
    resp = MessagingResponse()

    if user:
        emergency_contact = EmergencyContact.query.filter_by(user_hashed_id=user.hashed_id).first()
        
        if emergency_contact:
            resp.message("Welcome back! You’re logged in.")
        else:
            resp.message("To ensure your safety, please provide an emergency contact (e.g., 0570081720).")

    else:
        if incoming_msg.lower() == 'sign up':
            resp.message("Please reply with your full name and role (e.g., 'John Doe, passenger').")
        elif ',' in incoming_msg:
            try:
                name, role = [i.strip() for i in incoming_msg.split(',', 1)]
                
                if name and role:
                    new_user = User(name=name, role=role, whatsapp_number=from_number)
                    db.session.add(new_user)
                    db.session.commit()
                    resp.message("Thanks for signing up! You’re now logged in. To ensure your safety, please provide an emergency contact (e.g., 0570081720).")
                else:
                    resp.message("There was an error with your signup. Please make sure to include both your name and role separated by a comma.")
            except Exception as e:
                resp.message("There was an error with your signup. Please format as 'Full Name, role'.")

    if user and not emergency_contact and incoming_msg.isdigit() and len(incoming_msg) == 10:
        try:
            new_contact = EmergencyContact(user_hashed_id=user.hashed_id, contact_number=incoming_msg)
            db.session.add(new_contact)
            db.session.commit()
            resp.message("Emergency contact saved successfully.")
        except Exception as e:
            resp.message("There was an error saving your emergency contact. Please try again.")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)