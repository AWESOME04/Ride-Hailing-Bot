from config import app
from routes.whatsapp_routes import whatsapp_bp

app.register_blueprint(whatsapp_bp)

if __name__ == '__main__':
    app.run(debug=True)