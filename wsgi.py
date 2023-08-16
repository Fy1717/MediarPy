# postgres root pass --> fy1618
# postgres postgres password --> postgres

# !/usr/local/bin/python
# -*- coding: utf-16 -*-

from flask import jsonify
from app import createApp
from flask_cors import CORS
from app.initialize_db import createDB

from api.admins import apiAdmins
from api.users import apiUsers
from api.shares import apiShares

app = createApp()
CORS(app)
createDB()

app.register_blueprint(apiAdmins)
app.register_blueprint(apiUsers)
app.register_blueprint(apiShares)


@app.route("/")
def hello_world():
    return jsonify({"backend": "FY", "frontend": "OD"})

@app.route("/profile")
def profile():
    users = [
        {
            "id": "1",
            "name": "Furkan",
            "surname": "Yildiz",
            "birthday": "17.01.1997",
            "admin": True,
        },
        {
            "id": "2",
            "name": "Murat",
            "surname": "Yildiz",
            "birthday": "17.01.1997",
            "admin": True,
        },
    ]

    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8083)
