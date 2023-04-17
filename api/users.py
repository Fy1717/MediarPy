from flask import Blueprint, jsonify, request, session
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from app.jwtAuthorize import login_required

apiUsers = Blueprint("apiUsers", __name__, url_prefix="/api/users")
queries = User


@apiUsers.route("/")
@login_required
def users(current_user):
    try:
        results = queries.getAllUsers()

        users = []

        for user in results:
            users.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "image": user.image,
                    "birthday": user.birthday,
                    "admin": user.admin,
                    "activated": user.activated,
                    "following": len(user.following),
                    "followers": len(user.followers),
                    "countOfShares": len(user.pointed_shares)
                }
            )

        return jsonify({"data": users})
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error"})


@apiUsers.route("/<int:id>")
@login_required
def user(current_user, id):
    try:
        user = queries.getOneUser(id)

        print("USER POINTED SHARES : ", user.pointed_shares)

        idsOfPointedShares = []

        for share in user.pointed_shares:
            idsOfPointedShares.append(share.id)

        if user != None:
            result = {
                "id": user.id,
                "username": user.username,
                "image": user.image,
                "birthday": user.birthday,
                "admin": user.admin,
                "activated": user.activated,
                "email": user.email,
                "followings": [
                    {
                        "Id": followingUser.id,
                        "Username": followingUser.username,
                        "Email": followingUser.email,
                        "Image": followingUser.image,
                        "Birthday": followingUser.birthday,
                    }
                    for followingUser in user.following
                ],
                "followers": [
                    {
                        "Id": followerUser.id,
                        "Username": followerUser.username,
                        "Email": followerUser.email,
                        "Image": followerUser.image,
                        "Birthday": followerUser.birthday,
                    }
                    for followerUser in user.followers
                ],
                "starred_shares": idsOfPointedShares
            }

            if result["id"] != None or result["id"] != "":
                return jsonify({"data": result})
            else:
                return jsonify({"success": False})
        else:
            return jsonify({"success": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@apiUsers.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(current_user, id):
    try:
        if current_user.id == id:
            user = queries.getOneUser(id)

            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")
                image = request.form.get("image")
                birthday = request.form.get("birthday")
                email = request.form.get("email")
                admin = request.form.get("admin")

                if username != None:
                    usernameIsExist = queries.getUserByUsername(username)

                    if usernameIsExist != None:
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": "This username couldnt used, its already used",
                                }
                            ),
                            502,
                        )
                else:
                    username = user.username

                if password == None:
                    password = user.password
                else:
                    password = generate_password_hash(
                        password, method="sha256")

                if image == None:
                    image = user.image

                if birthday == None:
                    birthday = user.birthday

                if email == None:
                    email = user.email

                if admin == None:
                    admin = user.admin

                user = {
                    "id": id,
                    "username": username,
                    "image": image,
                    "birthday": birthday,
                    "password": password,
                    "email": email,
                    "admin": admin,
                }

                queries.updateUser(user)

                response = jsonify({"message": "User updated successfully"})
            else:
                response = (
                    jsonify(
                        {"success": False, "error": "This is not a post request"}),
                    400,
                )
        else:
            response = (
                jsonify(
                    {
                        "success": False,
                        "error": "You cant change another users information",
                    }
                ),
                401,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error"})


@apiUsers.route("/addUser", methods=["GET", "POST"])
def addUser():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            image = request.form.get("image")
            birthday = request.form.get("birthday")
            email = request.form.get("email")

            if (
                username != None
                and image != None
                and birthday != None
                and password != None
            ):
                hashed_password = generate_password_hash(
                    password, method="sha256")

                user = {
                    "username": username,
                    "image": image,
                    "birthday": birthday,
                    "password": hashed_password,
                    "email": email,
                }

                usernameIsExist = queries.getUserByUsername(username)

                if usernameIsExist != None:
                    response = jsonify(
                        {
                            "success": False,
                            "error": "This username couldnt used, its already used",
                        }
                    ), 
                else:
                    addProcess = queries.addUser(user)

                    response = jsonify({"message": addProcess})
            else:
                response = (
                    jsonify(
                        {"success": False, "error": "Some data is missed or empty"}
                    ),
                    502,
                )
        else:
            response = (
                jsonify({"success": False, "error": "This is not a post request"}),
                400,
            )

        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@apiUsers.route("/follow", methods=["GET", "POST"])
@login_required
def follow(current_user):
    try:
        if request.method == "POST":
            userId = request.args.get("userId")

            if current_user.id != None and userId != None:
                result = queries.follow(current_user.id, userId)

                return jsonify({"message": result})
            else:
                return jsonify({"success": False})
        else:
            return jsonify({"success": False, "error": "This is not a post request"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@apiUsers.route("/unfollow", methods=["GET", "POST"])
@login_required
def unfollow(current_user):
    try:
        if request.method == "POST":
            userId = request.args.get("userId")

            print("USER ID : ", userId)

            if current_user.id != None and userId != None:
                result = queries.unfollow(current_user.id, userId)

                return jsonify({"message": result})
            else:
                return jsonify({"success": False})
        else:
            return jsonify({"success": False, "error": "This is not a post request"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

@apiUsers.route("/point_share", methods=["GET", "POST"])
@login_required
def pointShare(current_user):
    try:
        if request.method == "POST":
            shareId = request.form.get("shareId")

            print("CURRENT USER ID : ", current_user.id)
            print("SHARE ID : ", shareId)

            if current_user.id != None and shareId != None:
                result = queries.point_share(current_user.id, shareId)

                return jsonify({"message": result})
            else:
                return jsonify({"success": False})
        else:
            return jsonify({"success": False, "error": "This is not a post request"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

@apiUsers.route("/point_share_back", methods=["GET", "POST"])
@login_required
def pointShareBack(current_user):
    try:
        if request.method == "POST":
            shareId = request.args.get("shareId")

            if current_user.id != None and shareId != None:
                result = queries.follow(current_user.id, shareId)

                return jsonify({"message": result})
            else:
                return jsonify({"success": False})
        else:
            return jsonify({"success": False, "error": "This is not a post request"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@apiUsers.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            print("XXXXXXXXXX")
            username = request.form.get("username")
            password = request.form.get("password")

            print("Username : ", username)
            print("Password : ", password)

            if username == None and password == None:
                print("yyyyyyyyy")
                return jsonify({"success": False})

            user = queries.getUserByUsername(username=username)

            if user != None:
                print("DB DEN GELEN USER IN PASSWORD U : ", user.password)
                print("İSTEKTEN GELEN PASSWORD : ", password)

                if check_password_hash(user.password, password):
                    print("user ıd ", user.id)

                    token = jwt.encode(
                        {
                            "id": user.id,
                            "exp": datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=30),
                        },
                        "mediar-secret",
                    )

                    print("TOKEN : " + token)

                    session["token"] = token

                    print("SESSION TOKEN : " + session["token"])

                    user = {"id": user.id, "username": user.username, "token": token, "email": user.email}

                    return jsonify({"data": user})
                else:
                    return jsonify({"success": False, "error": "Passwords not matched"})
            else:
                return jsonify({"success": False, "error": "User not found"})
        else:
            return jsonify({"success": False, "error": "This is not a Post request"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e) + " User couldnt login"})


@apiUsers.route("/logout")
@login_required
def logout(current_user):
    try:
        print("SESSION TOKEN : ", session["token"])
        session["token"] = "None"

        return jsonify({"description": "User Logout"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
