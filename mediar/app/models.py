from dataclasses import dataclass
from email.policy import default
from app import db
from datetime import date


# -------------------------------------------------------


@dataclass
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    image = db.Column(db.String(120))
    birthday = db.Column(db.DateTime, default=date.today())
    admin = db.Column(db.Boolean, default=False)
    activated = db.Column(db.Boolean, default=True)
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
    def addUser(cls, user):
        try:
            addingUser = cls(
                username=user["username"],
                image=user["image"],
                birthday=date.today(),
                admin=False,
                activated=True,
                password=user["password"],
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
            result.image = user["image"]
            result.birthday = user["birthday"]
            result.email = user["email"]
            result.password = user["password"]
            result.admin = bool(user["admin"])

            # print("RESULT.ADMIN : ", result.admin, " TYPE : ", type(result.admin))

            db.session.commit()

            return "updated"

        except Exception as e:
            print("ERROR --> ", e)

            return "not updated"

    @classmethod
    def follow(cls, user_id, following_id):
        try:
            user = cls.query.get(user_id)
            following = cls.query.get(following_id)

            user.following.append(following)
            db.session.commit()

            return "followed"
        except Exception as e:
            print("HATA --> ", e)

            return "not followed"

    @classmethod
    def unfollow(cls, user_id, following_id):
        try:
            user = cls.query.get(user_id)
            following = cls.query.get(following_id)

            user.following.remove(following)
            db.session.commit()

            return "unfollowed"
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


user_following = db.Table(
    "user_following",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey(User.id), primary_key=True),
    db.Column("following_id", db.Integer, db.ForeignKey(User.id), primary_key=True),
)


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
        except Exception as e:
            result = {}

            print("ERROR --> ", e)

        return result
