from config import app
from routes.whatsapp_routes import whatsapp_bp
import os

app.register_blueprint(whatsapp_bp)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)