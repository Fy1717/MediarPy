from flask import Blueprint, jsonify, request
from app.models import Share
from app.jwtAuthorize import login_required

apiShares = Blueprint("apiShares", __name__, url_prefix="/api/shares")
queries = Share


@apiShares.route("/")
def shares():
    try:
        results = queries.getAllShares()

        shares = []

        for share in results:
            shares.append(
                {
                    "id": share.id,
                    "content": share.content,
                    "point": share.point,
                    "author_id": share.author,
                }
            )

        return jsonify({"data": shares, "count": len(shares)})
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/<int:id>")
def share(id):
    try:
        result = queries.getOneShare(id)
        share = {}

        if result != None:
            share = {
                "id": result.id,
                "content": result.content,
                "point": result.point,
                "authorId": result.author,
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
                addProcess = queries.addShare(share)

                response = jsonify({"message": addProcess})
            else:
                response = jsonify(
                    {"success": False, "error": "There is an error.."})
        else:
            response = (
                jsonify(
                    {"success": False, "error": "This is not a post request.."}),
                400,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502


@apiShares.route("/sharesOfAuthor/<int:author_id>")
def sharesOfAuthor(author_id):
    try:
        results = queries.sharesOfAuthor(author_id)

        shares = []

        for share in results:
            shares.append(
                {
                    "id": share.id,
                    "content": share.content,
                    "point": share.point,
                    "author": share.author,
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

            updatingShare = queries.getOneShare(id)

            if updatingShare.author == int(authorId):
                if content == None:
                    content = updatingShare.content
                if point == None:
                    point = updatingShare.point

                share = {"id": id, "content": content, "point": point}
                addProcess = queries.updateShare(share)

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
                400,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error.."}), 502
