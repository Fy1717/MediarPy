from app.models import db
from app import createApp

def createDB():
    app = createApp()
    
    with app.app_context():
        db.create_all()
