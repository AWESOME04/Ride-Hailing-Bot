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
        resp.message("Welcome back! You’re logged in.")
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
                    resp.message("Thanks for signing up! You’re now logged in.")
                else:
                    resp.message("There was an error with your signup. Please make sure to include both your name and role separated by a comma.")
            except Exception as e:
                # print("Signup error:", e)
                resp.message("There was an error with your signup. Please format as 'Full Name, role'.")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
