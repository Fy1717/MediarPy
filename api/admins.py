from flask import Blueprint, jsonify, request
from app.jwtAuthorize import login_required
from app.models import User

apiAdmins = Blueprint("apiAdmins", __name__, url_prefix="/api/admins")
queries = User


@apiAdmins.route("/")
@login_required
def admins(current_user):
    try:
        currentUserIsAdmin = queries.getOneUser(current_user.id)

        if currentUserIsAdmin.admin == True:
            results = queries.getAllAdmins()

            admins = []

            for admin in results:
                admins.append(
                    {
                        "id": admin.id,
                        "username": admin.username,
                        "name": admin.name,
                        "email": admin.email,
                        "image": admin.image,
                        "birthday": admin.birthday,
                        "admin": admin.admin,
                        "activated": admin.activated,
                        "following": len(admin.following),
                        "followers": len(admin.followers),
                    }
                )

            response = {"data": admins, "count": len(admins)}
        else:
            response = {"success": False,
                        "error": "Only admin see all admins"}, 401

        return jsonify(response)
    except Exception as e:
        response = {"success": False, "error": "Admin is not found"}, 404

        return jsonify(response)


@apiAdmins.route("/<int:id>")
@login_required
def admin(current_user, id):
    try:
        currentUserIsAdmin = queries.getOneUser(current_user.id)

        if currentUserIsAdmin.admin == True:
            admin = queries.getOneAdmin(id)

            if admin != None:
                result = {
                    "id": admin.id,
                    "username": admin.username,
                    "name": admin.username,
                    "image": admin.image,
                    "birthday": admin.birthday,
                    "admin": admin.admin,
                    "activated": admin.activated,
                    "email": admin.email,
                    "followings": [
                        {
                            "Id": followingUser.id,
                            "Username": followingUser.username,
                            "Name": followingUser.name,
                            "Email": followingUser.email,
                            "Image": followingUser.image,
                            "Birthday": followingUser.birthday,
                        }
                        for followingUser in admin.following
                    ],
                    "followers": [
                        {
                            "Id": followerUser.id,
                            "Username": followerUser.username,
                            "Name": followerUser.name,
                            "Email": followerUser.email,
                            "Image": followerUser.image,
                            "Birthday": followerUser.birthday,
                        }
                        for followerUser in admin.followers
                    ],
                }

                if result["admin"] == True and (
                    result["id"] != None or result["id"] != ""
                ):
                    response = jsonify({"data": result})
                else:
                    response = (
                        jsonify(
                            {"success": False, "error": "Admin is not found"}),
                        404,
                    )
            else:
                response = (
                    jsonify({"success": False, "error": "Admin is not found"}),
                    404,
                )
        else:
            response = (
                jsonify({"success": False, "error": "Only admin see any admin"}),
                401,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 502


@apiAdmins.route("/makeadmin", methods=["GET", "POST"])
@login_required
def makeadmin(current_user):
    try:
        if request.method == "POST":
            id = request.args.get("id")

            user = queries.getOneUser(id)
            currentUserIsAdmin = queries.getOneUser(current_user.id)

            if currentUserIsAdmin.id != None and currentUserIsAdmin.admin == True:
                if user != None:
                    isUserAdmin = user.admin

                    if isUserAdmin == False:
                        queries.makeadmin(id)

                        response = jsonify(
                            {"message": "User updated to admin"})
                    else:
                        response = (
                            jsonify(
                                {"success": False, "error": "User already make admin"}
                            ),
                            400,
                        )
                else:
                    response = (
                        jsonify({"success": False, "error": "User not found"}),
                        404,
                    )
            else:
                response = (
                    jsonify(
                        {"success": False, "error": "Only an admin make admin a user"}
                    ),
                    404,
                )
        else:
            response = (
                jsonify({"success": False, "error": "This is not a post request"}),
                400,
            )

        return response
    except Exception as e:
        return jsonify({"success": False})
