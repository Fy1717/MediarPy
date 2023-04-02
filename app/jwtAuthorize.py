import jwt
from functools import wraps
from flask import jsonify, request, session
from app.models import User

queries = User()


""" def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "token" in session or "token" in request.headers:
            if "token" in session:
                print("-------token in session-------")
                token = session["token"]
                print("token session --> ", token)

            if "token" in request.headers:
                print("-------token in headers-------")
                token = request.headers["token"]
                print("token headers --> ", token)
        else:
            session["token"] = "None"
            token = session["token"]

        if token == "None":
            print("------- token none -------------")
            return (
                jsonify({"success": False, "error": "Please login the system.."}),
                401,
            )

        try:
            if jwt.decode(token, "mediar-secret", algorithms=["HS256"]) and ("token" in request.headers):
                token = request.headers["token"]
                dataDef = jwt.decode(token, "mediar-secret-def")

                if dataDef["id"] == "mediar-secret-def":
                    current_user = {"id": 0, "name": "mediar"}

            if jwt.decode(token, "mediar-secret", algorithms=["HS256"]):
                data = jwt.decode(token, "mediar-secret", algorithms=["HS256"])
                current_user = queries.getOneUser(id=data["id"])
                print("id: ", current_user.id,
                      "\nusername: ", current_user.username)

            if current_user == None:
                return (
                    jsonify(
                        {"success": False, "error": "Please login the system.."}),
                    401,
                )
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(e) + " - Signature has expired, please login the system..",
                    }
                ),
                401,
            )

        return f(current_user, *args, **kwargs)

    return decorator """


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        current_user = None

        if "token" in session:
            print("-------token in session-------")
            token = session["token"]
            print("token session --> ", token)
        elif "token" in request.headers:
            print("-------token in headers-------")
            token = request.headers["token"]
            print("token headers --> ", token)
        else:
            session["token"] = "None"
            token = session["token"]

        if token == "None":
            print("------- token none -------------")
            error_message = {"success": False, "error": "Please login the system.."}
            return jsonify(error_message), 401

        try:
            data = jwt.decode(token, "mediar-secret", algorithms=["HS256"])
            current_user = queries.getOneUser(id=data["id"])
            print("id: ", current_user.id, "\nusername: ", current_user.username)
        except jwt.ExpiredSignatureError:
            error_message = {
                "success": False,
                "error": "Signature has expired, please login the system..",
            }
            return jsonify(error_message), 401
        except jwt.InvalidTokenError:
            error_message = {"success": False, "error": "Invalid token"}
            return jsonify(error_message), 401
        except Exception as e:
            error_message = {"success": False, "error": str(e)}
            return jsonify(error_message), 401

        if current_user is None:
            error_message = {"success": False, "error": "Please login the system.."}
            return jsonify(error_message), 401

        return f(current_user, *args, **kwargs)

    return decorator
