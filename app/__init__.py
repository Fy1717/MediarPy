from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from sqlalchemy import create_engine

db = SQLAlchemy()
database_uri = "postgresql://postgres:postgres@localhost:5432/mediar"

engine = create_engine(database_uri, echo=True)


def createApp():
    app = Flask(__name__, static_url_path="")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/"
    app.config["SECRET_KEY"] = "mediar-secret"
    app.config["SECRET_KEY_DEF"] = "mediar-secret-def"

    CORS(app)

    db.init_app(app)

    return app
