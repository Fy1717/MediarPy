from app.models import db
from app import createApp
from sqlalchemy import create_engine

SQLALCHEMY_TRACK_MODIFICATIONS = True

engine = create_engine('postgresql://postgres:postgres@db:5432/mediar', echo=True)

def createDB():
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    create_engine('postgresql://postgres:postgres@db:5432/mediar', echo=True)

    db.create_all(app=createApp())


createDB()
