from app.models import db
from app import createApp


def createDB():
    db.create_all(app=createApp())


createDB()
