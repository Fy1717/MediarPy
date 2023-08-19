from flask import Blueprint, jsonify, request, session
from app.models import User, Share
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from app.jwtAuthorize import login_required
import traceback


apiUsers = Blueprint("apiUsers", __name__, url_prefix="/api/users")
queries = User
shareQueries = Share


@apiUsers.route("/")
@login_required
def users(current_user):
    try:
        print("Current User : ", current_user.admin)

        if current_user.admin:
            results = queries.getAllUsers()

            users = []

            for user in results:
                users.append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
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
        else:
            return jsonify({"success": False, "error": "User is not admin"})

        return jsonify({"data": users})
    except Exception as e:
        return jsonify({"success": False, "error": "There is an error"})


@apiUsers.route("/<int:id>")
@login_required
def user(current_user, id):
    try:
        user = queries.getOneUser(id)

        result = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "image": user.image,
            "birthday": user.birthday,
            "admin": user.admin,
            "activated": user.activated,
            "email": user.email,
            "followings": [
                {
                    "Id": followingUser.id,
                    "Username": followingUser.username,
                    "Name": followingUser.name,
                    "Email": followingUser.email,
                    "Image": followingUser.image,
                    "Birthday": followingUser.birthday,
                    "FollowingsShares": getShareListOfUser(followingUser.id)
                }
                for followingUser in user.following
            ],
            "followers": [
                {
                    "Id": followerUser.id,
                    "Username": followerUser.username,
                    "Name": followerUser.name,
                    "Email": followerUser.email,
                    "Image": followerUser.image,
                    "Birthday": followerUser.birthday,
                    "FollowersShares": getShareListOfUser(followerUser.id),
                }
                for followerUser in user.followers
            ],
            "shares": getShareListOfUser(user.id),
            "starred_shares": [
                {
                    "Id": share.id,
                    "Content": share.content,
                    "Point": share.point,
                }
                for share in user.pointed_shares
            ]
        }

        if result["id"] != None or result["id"] != "":
            return jsonify({"data": result})
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
                name = request.form.get("name")
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

                if name == None:
                    name = user.name

                user = {
                    "id": id,
                    "username": username,
                    "name": name,
                    "image": image,
                    "birthday": birthday,
                    "password": password,
                    "email": email,
                    "admin": admin,
                }

                updateMessageFromDbProcess = queries.updateUser(user)

                if updateMessageFromDbProcess == "User Updated Successfully":
                    response = jsonify({"message": updateMessageFromDbProcess})
                else:
                    response = (
                        jsonify(
                            {"success": False, "error": "There is an error for update user"}),
                        400,
                    )
            else:
                response = (
                    jsonify(
                        {"success": False, "error": "This is not a post request"}),
                    405,
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
            name = request.form.get("name")
            password = request.form.get("password")
            image = request.form.get("image")
            birthday = request.form.get("birthday")
            email = request.form.get("email")

            if (
                username != None
                and image != None
                and birthday != None
                and password != None
                and name != None
            ):
                hashed_password = generate_password_hash(
                    password, method="sha256")

                user = {
                    "username": username,
                    "name": name,
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
                405,
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

            print("USER ID : ", userId)
            print("CURRENT USER ID : ", current_user.id)

            if current_user.id != None and userId != None:
                if str(current_user.id) == str(userId):
                    return jsonify({"success": False, "error": "User cannot self-follow"}), 502 
                else:
                    result = queries.follow(current_user.id, userId)

                    if result == "followed":
                        return jsonify({"message": result}), 200
                    elif result == "already followed":
                        return jsonify({"success": False, "error": result}), 502
                    else:
                        return jsonify({"success": False, "error": "There is an error :("}), 503
            else:
                return jsonify({"success": False, "error": "There is an error :("}), 502
        else:
            return jsonify({"success": False, "error": "This is not a post request"}), 405

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 502


@apiUsers.route("/unfollow", methods=["GET", "POST"])
@login_required
def unfollow(current_user):
    try:
        if request.method == "POST":
            userId = request.args.get("userId")

            print("USER ID : ", userId)
            print("CURRENT USER ID : ", current_user.id)

            if current_user.id == userId:
                return jsonify({"success": False, "error": "User cannot self-unfollow"}), 502 
            
            if current_user.id != None and userId != None:
                if str(current_user.id) == str(userId):
                    return jsonify({"success": False, "error": "User cannot self-unfollow"}), 502 
                else:
                    result = queries.unfollow(current_user.id, userId)

                    if result == "unfollowed":
                        return jsonify({"message": result})
                    elif result == "user not followed yet":
                        return jsonify({"success": False, "error": "User not followed yet"}), 403
            else:
                return jsonify({"success": False, "message": "There is an error :("}), 502
        else:
            return jsonify({"success": False, "error": "This is not a post request"}), 405

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 502


@apiUsers.route("/point_share", methods=["GET", "POST"])
@login_required
def pointShare(current_user):
    try:
        if request.method == "POST":
            shareId = request.form.get("shareId")

            print("CURRENT USER ID : ", current_user.id)
            print("SHARE ID : ", shareId)

            if current_user.id != None and shareId != None:  # kullanıcı kendi paylaşını beğenemesin amacı ile
                print("shareId : ", shareId)

                result = queries.point_share(current_user.id, shareId)

                if result == "pointed successfully":

                    return jsonify({"message": result})
                else:
                    if result == "user cannot pointed him shares":
                        return jsonify({"success": False, "error": result}), 401
                    else:
                        return jsonify({"success": False, "error": "There is an error :("}), 502
            else:
                return jsonify({"success": False, "error": "There is an error :("}), 502
        else:
            return jsonify({"success": False, "error": "This is not a post request"}), 405

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 503


@apiUsers.route("/point_share_back", methods=["GET", "POST"])
@login_required
def pointShareBack(current_user):
    try:
        if request.method == "POST":
            shareId = request.form.get("shareId")

            print("CURRENT USER ID : ", current_user.id)
            print("SHARE ID : ", shareId)
            
            print("CHECK : ", (current_user.id != None and shareId != None))
            print("CHECK : ", (current_user.id), shareId)
            
            if current_user.id != None and shareId != None:
                result = queries.point_share_back(current_user.id, shareId)

                if result == "pointed back successfully":
                    return jsonify({"success": True, "message": result})
                else:
                    return jsonify({"success": False, "error": "There is an error 1 :("}), 502
            else:
                return jsonify({"success": False, "error": "There is an error :( 2"}), 502
        else:
            return jsonify({"success": False, "error": "This is not a post request"}), 405

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 503


@apiUsers.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == None and password == None:
                return jsonify({"success": False})

            user = queries.getUserByUsername(username=username)

            if user != None:
                if check_password_hash(user.password, password):
                    token = jwt.encode(
                        {
                            "id": user.id,
                            "exp": datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=30),
                        },
                        "mediar-secret",
                    )

                    session["token"] = token

                    followings = []
                    followers = []
                    followingsIdList = []
                    followersIdList = []
                    shareListOfUser = getShareListOfUser(user.id)

                    try:
                        for followingUser in user.following:
                            followings.append(getConnectingUserInfo(followingUser.id))
                            followingsIdList.append(followingUser.id)

                        for followerUser in user.followers:
                            followers.append(getConnectingUserInfo(followerUser.id))
                            followersIdList.append(followerUser.id)

                        starredUserList = []

                        starredShareList = []
                        for share in user.pointed_shares:
                            starredShareList.append({
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
                            })
                            

                        totalPoints = len(starredUserList)

                        user = {
                            "id": user.id,
                            "name": user.name,
                            "username": user.username,
                            "token": token,
                            "email": user.email,
                            "image": user.image,
                            "followings": followings,
                            "followers": followers,
                            "shares": shareListOfUser,
                            "totalPoints": totalPoints,
                            "starred_shares": starredShareList,
                        }

                        response = {"success": True, "data": user, "message": ""}

                        print("RESPONSE :: ", response)

                        return jsonify(response)
                    except Exception as e:
                        print("ERROR0 : ", str(e))

                        return jsonify({"message": "There is a problem :("}), 503
                else:
                    return jsonify({"message": "Passwords not matched"}), 401
            else:
                return jsonify({"message": "User not found"}), 401
        else:
            return jsonify({"message": "This is not a Post request"}), 405
    except Exception as e:
        print("ERROR1 : ", str(e))

        return jsonify({"message": "There is a problem :("}), 503


@apiUsers.route("/logout")
@login_required
def logout(current_user):
    try:
        session["token"] = "None"

        return jsonify({"success": True, "message": "User Logout"})
    except Exception as e:
        error_message = f"Logout Process Error: {e}\n{traceback.format_exc()}"
        
        print(error_message)

        return jsonify({"error": error_message}), 503
    
def getShareListOfUser(userId):
    shareListOfUser = []
    sharesOfUser = shareQueries.sharesOfAuthor(userId)

    for share in sharesOfUser:
        shareListOfUser.append({
            "Id": share.id,
            "Content": share.content,
            "Point": len(share.pointed_users)
        })

    return shareListOfUser

@apiUsers.route("/sharesOfFollowedUsers/<int:id>", methods=["GET", "POST"])
@login_required
def getShareListOfUsers(current_user, id):
    if current_user.id == id:        
        user = queries.getOneUser(id)
        
        userIdList = []
        allShares = []
            
        print("FOLLOWING USERS : ", user.following)
        
        if len(user.following) == 0:
            return jsonify({"data": []}), 200
        
        for followingUser in user.following:
            userIdList.append(followingUser.id)
        
        for userId in userIdList:
            shareListOfUser = []
            sharesOfUser = shareQueries.sharesOfAuthor(userId)

            for share in sharesOfUser:
                shareListOfUser.append({
                    "Id": share.id,
                    "UserId": userId,
                    "Content": share.content,
                    "Point": len(share.pointed_users)
                })
                
            allShares.append(shareListOfUser)

        return allShares
    
    else:
        response = (
            jsonify(
                {
                    "success": False,
                    "error": "You cant see another users information",
                }
            ),
            401,
        )
        
        return response

def getConnectingUserInfo(userId):
    userFromDb = queries.getOneUser(userId)
    
    user = {
        "Id": userFromDb.id,
        "Username": userFromDb.username,
        "Name": userFromDb.name,
        "Email": userFromDb.email,
        "Image": userFromDb.image,
        "Birthday": userFromDb.birthday,
        "Shares": getShareListOfUser(userId)
    }
    
    return user

