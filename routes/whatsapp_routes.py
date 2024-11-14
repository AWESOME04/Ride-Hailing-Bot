from flask import Blueprint, request
from handlers.message_handler import MessageHandler

whatsapp_bp = Blueprint('whatsapp', __name__)
message_handler = MessageHandler()

@whatsapp_bp.route('/', methods=['GET'])
def home():
    return "Hello, this is your WhatsApp bot!"

@whatsapp_bp.route('/whatsapp', methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '').strip()
    return message_handler.handle_message(incoming_msg, from_number)