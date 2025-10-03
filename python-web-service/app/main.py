from flask import Flask
from app.routes import main as main_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_routes)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)