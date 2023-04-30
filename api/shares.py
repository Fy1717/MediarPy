from flask import Blueprint, jsonify, request
from app.models import Share
from app.models import User
from app.jwtAuthorize import login_required

apiShares = Blueprint("apiShares", __name__, url_prefix="/api/shares")
shareQueries = Share
userQueries = User


@apiShares.route("/")
def shares():
    try:
        results = shareQueries.getAllShares()

        shares = []

        for share in results:
            shares.append(
                {
                    "id": share.id,
                    "content": share.content,
                    "point": share.point,
                    "author_id": share.author,
                    "pointed_users": [
                        {
                            "user_id": pointedUser.id,
                            "username": pointedUser.username,
                        }
                        for pointedUser in share.pointed_users
                    ]
                }
            )

        return jsonify({"data": shares, "count": len(shares)})
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/<int:id>")
def share(id):
    try:
        result = shareQueries.getOneShare(id)
        share = {}

        if result != None:
            share = {
                "id": result.id,
                "content": result.content,
                "point": result.point,
                "authorId": result.author,
                "pointed_users": [
                    {
                        "user_id": pointedUser.id,
                        "username": pointedUser.username,
                    }
                    for pointedUser in result.pointed_users
                ]
            }

            response = jsonify({"data": share})
        else:
            response = jsonify(
                {"success": False, "error": "Share is not found"}), 404

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/addShare", methods=["GET", "POST"])
@login_required
def addShare(current_user):
    try:
        if request.method == "POST":
            content = request.form.get("content")

            if content != None and current_user.id != None:
                share = {"content": content, "authorId": current_user.id}
                addProcess = shareQueries.addShare(share)

                response = jsonify({"message": addProcess})
            else:
                response = jsonify(
                    {"success": False, "error": "There is an error.."})
        else:
            response = (
                jsonify(
                    {"success": False, "error": "This is not a post request.."}),
                405,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/sharesOfAuthor/<int:author_id>")
def sharesOfAuthor(author_id):
    try:
        results = shareQueries.sharesOfAuthor(author_id)
        print("aa : ", results)
        print("bb : ", results[0].pointed_users)
        print("cc : ", results[0].pointed_users[1].id)

        shares = []

        for share in results:
            shares.append(
                {
                    "id": share.id,
                    "content": share.content,
                    "point": share.point,
                    "author": share.author,
                    "pointed_users_count": len(share.pointed_users),
                    "pointed_users": [
                        {
                            "user_id": pointedUser.id,
                            "username": pointedUser.username,
                        }
                        for pointedUser in share.pointed_users
                    ]
                }
            )

        return jsonify({"data": shares, "count": len(shares)})
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/update", methods=["GET", "POST"])
@login_required
def update(current_user):
    try:
        if request.method == "POST":
            id = request.form.get("id")
            content = request.form.get("content")
            point = request.form.get("point")
            authorId = current_user.id

            updatingShare = shareQueries.getOneShare(id)

            if updatingShare.author == int(authorId):
                if content == None:
                    content = updatingShare.content
                if point == None:
                    point = updatingShare.point

                share = {"id": id, "content": content, "point": point}
                addProcess = shareQueries.updateShare(share)

                response = jsonify({"message": addProcess})
            else:
                response = (
                    jsonify(
                        {"success": False, "error": "Cannot change another users share"}
                    ),
                    401,
                )
        else:
            response = (
                jsonify({"success": False, "error": "This is not a post request"}),
                405,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502
