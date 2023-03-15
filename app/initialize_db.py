from app.models import db
from app import createApp
from sqlalchemy import create_engine

def createDB():
    app = createApp()
    
    with app.app_context():
        db.create_all()
