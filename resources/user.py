from datetime import date

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)

from passlib.hash import pbkdf2_sha256

from models import UserModel, StaffModel, db
from schemas import UserSchema
from blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operations on users")


def _ensure_admin():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        abort(403, message="Admin privilege required.")


def _staff_work_email(username: str, user_id: int) -> str:
    return f"{username}.{user_id}@staff.local"


def _create_staff_for_user(user: UserModel):
    staff = StaffModel(
        first_name=user.username[:30],
        last_name="Staff",
        date_of_birth=date(1970, 1, 1),
        work_phone=f"0207{user.id:07d}",
        mobile_phone=f"07123{user.id:06d}",
        work_email=_staff_work_email(user.username, user.id),
        position="Staff",
        user_id=user.id,
    )
    db.session.add(staff)


def _sync_staff_for_user(user: UserModel):
    if not user.staff:
        _create_staff_for_user(user)
        return

    user.staff.first_name = user.username[:30]
    user.staff.work_email = _staff_work_email(user.username, user.id)


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.find_by_username(user_data["username"]):
            abort(400, message="A user with that username already exists.")

        user = UserModel()
        user.username=user_data["username"]
        user.password=pbkdf2_sha256.hash(user_data["password"])

        db.session.add(user)
        db.session.flush()
        _create_staff_for_user(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.find_by_username(user_data["username"])

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Store identity as string to satisfy PyJWT's requirement that "sub" be a string
            identity = str(user.id)
            access_token = create_access_token(identity=identity, fresh=True)
            refresh_token = create_refresh_token(identity)
            print("ISSUED ACCESS TOKEN:", access_token)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        _ensure_admin()
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        _ensure_admin()
        users = UserModel.query.all()
        return users


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        _ensure_admin()
        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")
        return user

    @jwt_required()
    def delete(self, user_id):
        _ensure_admin()
        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")
        if user.staff:
            db.session.delete(user.staff)
        user.delete_from_db()
        return {"message": "User deleted."}, 200

    @jwt_required()
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        _ensure_admin()
        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")

        new_username = user_data.get("username")
        if new_username and new_username != user.username:
            existing = UserModel.find_by_username(new_username)
            if existing and existing.id != user.id:
                abort(400, message="A user with that username already exists.")
            user.username = new_username

        new_password = user_data.get("password")
        if new_password:
            user.password = pbkdf2_sha256.hash(new_password)

        _sync_staff_for_user(user)
        db.session.commit()

        return user


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        _ensure_admin()
        current_user = get_jwt_identity()
        # Identity was stored as string, keep it as such when issuing a new access token
        new_token = create_access_token(identity=str(current_user), fresh=False)
        return {"access_token": new_token}, 200
