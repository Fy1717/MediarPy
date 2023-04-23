import jwt
from functools import wraps
from flask import jsonify, request, session
from app.models import User

queries = User()


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        current_user = None

        if "token" in session and str(token) != "None":
            print("-------token in session-------")
            token = session["token"]
            print("token session --> ", token)
        elif "token" in request.headers:
            print("-------token in headers-------")
            token = request.headers["token"]

            if token == None:
                token = request.headers.get("token")

            print("token headers --> ", token)
        else:
            session["token"] = "None"
            token = session["token"]

        if token == "None":
            print("------- token none -------------")
            error_message = {"success": False,
                             "error": "Please login the system.."}
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
            error_message = {"success": False,
                             "error": "Please login the system.."}
            return jsonify(error_message), 401

        return f(current_user, *args, **kwargs)

    return decorator
