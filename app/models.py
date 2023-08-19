from dataclasses import dataclass
from email.policy import default
from app import db
from datetime import date
import traceback;

# -------------------------------------------------------

@dataclass
class Share(db.Model):
    __tablename__ = "share"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    author = db.Column(db.Integer, db.ForeignKey("user.id"))
    point = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, default=date.today())

    def __init__(self, content, author, point, created_date):
        self.content = content
        self.point = point
        self.author = author
        self.created_date = created_date

    @classmethod
    def getAllShares(cls):
        try:
            results = cls.query.all()
        except Exception as e:
            print("ERROR --> ", e)

            results = []

        return results

    @classmethod
    def addShare(cls, share):
        try:
            addingShare = cls(
                content=share["content"],
                point=0,
                author=share["authorId"],
                created_date=date.today(),
            )

            db.session.add(addingShare)
            db.session.commit()

            return "Share added successfully"
        except Exception as e:
            print("ERROR --> ", e)

            return "Share could not added"

    @classmethod
    def getOneShare(cls, id):
        try:
            result = cls.query.get(id)
        except Exception as e:
            result = {}
            print("ERROR --> ", e)

        return result

    @classmethod
    def updateShare(cls, share):
        try:
            result = cls.query.get(share["id"])
            result.content = share["content"]
            result.point = share["point"]

            db.session.commit()

            return "Share update successfully"
        except Exception as e:
            return "Share update error"

    @classmethod
    def sharesOfAuthor(cls, author_id):
        try:
            result = cls.query.filter_by(author=author_id).all()
            print("---- shares of author : ", result, " ----")
        except Exception as e:
            result = []

            print("ERROR --> ", e)

            return []

        return result

@dataclass
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    image = db.Column(db.String(500))
    birthday = db.Column(db.DateTime, default=date.today())
    admin = db.Column(db.Boolean, default=False)
    activated = db.Column(db.Boolean, default=True)
    pointed_shares = db.relationship(
        "Share",
        lambda: user_pointed_shares,
        primaryjoin=lambda: User.id == user_pointed_shares.c.user_id,
        secondaryjoin=lambda: Share.id == user_pointed_shares.c.share_id,
        backref="pointed_users",
    )

    following = db.relationship(
        "User",
        lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.user_id,
        secondaryjoin=lambda: User.id == user_following.c.following_id,
        backref="followers",
    )

    @classmethod
    def getAllUsers(cls):
        try:
            results = cls.query.all()
        except Exception as e:
            print("ERROR --> ", e)
            results = []

        return results
    
    @classmethod
    def get_followed_users_shares(cls):
        followed_users = cls.following 
        followed_users_ids = [user.id for user in followed_users]

        followed_users_shares = Share.query.filter(Share.author.in_(followed_users_ids)).all()

        return followed_users_shares

    @classmethod
    def addUser(cls, user):
        try:
            addingUser = cls(
                username=user["username"],
                name=user["name"],
                image=user["image"],
                birthday=date.today(),
                admin=False,
                activated=True,
                password=user["password"],
                email=user["email"]
            )

            db.session.add(addingUser)
            db.session.commit()

            return "New User Added.."
        except Exception as e:
            print("ERROR --> ", e)

            return "User couldnt be added.."

    @classmethod
    def getOneUser(cls, id):
        try:
            result = cls.query.get(id)
        except Exception as e:
            print("ERROR --> ", e)
            result = {}

        return result

    @classmethod
    def updateUser(cls, user):
        try:
            result = cls.query.get(user["id"])

            result.username = user["username"]
            result.name =user["name"]
            result.image = user["image"]
            result.birthday = user["birthday"]
            result.email = user["email"]
            result.password = user["password"]
            result.admin = bool(user["admin"])

            # print("RESULT.ADMIN : ", result.admin, " TYPE : ", type(result.admin))

            db.session.commit()

            return "User Updated Successfully"

        except Exception as e:
            print("ERROR --> ", e)

            return "There is an error for update user"

    @classmethod
    def follow(cls, user_id, following_id):
        try:
            user = cls.query.get(user_id)
            following = cls.query.get(following_id)

            alreadyFollowedList = []

            print("\n--- user_id : ", user_id, " ----")
            print("--- following_id : ", following_id, " ----")
            print("following list size : ", len(user.following))

            for followingUser in user.following:
                alreadyFollowedList.append(followingUser.id)

            print("followed list : ", alreadyFollowedList)

            if following.id in alreadyFollowedList:
                print("already in followings..")

                return "already followed"
            else:
                user.following.append(following)

                db.session.commit()

                return "followed"
                
        except Exception as e:
            print("HATA 1 --> ", e)

            return "not followed"

    @classmethod
    def unfollow(cls, user_id, following_id):
        try:
            user = cls.query.get(user_id)
            following = cls.query.get(following_id)

            if following in user.following:
                user.following.remove(following)
                db.session.commit()

                return "unfollowed"
            else:
                return "user not followed yet"
        except Exception as e:
            print("ERROR --> ", e)

            return "couldnt unfollow"

    @classmethod
    def getUserByUsername(cls, username):
        try:
            result = cls.query.filter_by(username=username).first()

            return result
        except Exception as e:
            print("ERROR --> ", e)

            return "user not founded"

    @classmethod
    def getAllAdmins(cls):
        try:
            results = cls.query.filter_by(admin=True).all()

            print("RESULT ADMINS : ", results)
        except Exception as e:
            print("ERROR --> ", e)
            results = []

        return results

    @classmethod
    def getOneAdmin(cls, id):
        try:
            result = cls.query.get(id)
        except Exception as e:
            print("ERROR --> ", e)

        return result

    @classmethod
    def makeadmin(cls, id):
        try:
            result = cls.query.get(id)
            result.admin = True
            db.session.commit()
        except Exception as e:
            print("ERROR --> ", e)

            return "not updated"

    @classmethod
    def point_share(cls, user_id, share_id):
        try:
            user = cls.query.get(user_id)
            share = Share.query.get(share_id)

            if user.id != share.author:
                print("DB .. user : ", user)
                print("DB .. share : ", share_id)
                print("DB .. star table : ", user.pointed_shares)

                print("user.pointed_shares : ", user.pointed_shares)

                user.pointed_shares.append(share)

                db.session.commit()

                return "pointed successfully"
            else:
                return "user cannot pointed him shares"
        except Exception as e:
            error_message = f"Star Share Process Error: {e}\n{traceback.format_exc()}"
                
            print("HATA 2 --> ", error_message)

            return "not pointed"

    @classmethod
    def point_share_back(cls, user_id, share_id):
        try:
            user = cls.query.get(user_id)
            share = Share.query.get(share_id)

            print("user.pointed_shares : ", user.pointed_shares)
            
            user.pointed_shares.remove(share)
            db.session.commit()

            return "pointed back successfully"
        except Exception as e:
            error_message = f"Star Share Process Error: {e}\n{traceback.format_exc()}"
                    
            print("ERROR --> ", error_message)

            return "couldnt back point"

user_following = db.Table(
    "user_following",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey(User.id), primary_key=True),
    db.Column("following_id", db.Integer,
              db.ForeignKey(User.id), primary_key=True),
)

user_pointed_shares = db.Table(
    "user_pointed_shares",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey(User.id), primary_key=True),
    db.Column("share_id", db.Integer, db.ForeignKey(
        Share.id), primary_key=True),
)

