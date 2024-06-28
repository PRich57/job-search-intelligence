from flask import Flask
from app.api.routes import create_api_routes

def create_app():
    app = Flask(__name__)
    create_api_routes(app)
    return app