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
from sqlalchemy.exc import IntegrityError

from passlib.hash import pbkdf2_sha256

from models import UserModel, StaffModel, db
from schemas import UserSchema, UserCreateSchema, UserUpdateSchema
from blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operations on users")


def _ensure_admin():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        abort(403, message="Admin privilege required.")


def _staff_work_email(username: str, user_id: int) -> str:
    return f"{username}.{user_id}@staff.local"


def _validate_staff_unique_fields(
    work_phone: str,
    mobile_phone: str,
    work_email: str,
    exclude_user_id: int | None = None,
):
    existing_work_phone = StaffModel.query.filter_by(work_phone=work_phone).first()
    if existing_work_phone and existing_work_phone.user_id != exclude_user_id:
        abort(400, message="Work phone already exists for another staff record.")

    existing_mobile_phone = StaffModel.query.filter_by(mobile_phone=mobile_phone).first()
    if existing_mobile_phone and existing_mobile_phone.user_id != exclude_user_id:
        abort(400, message="Mobile phone already exists for another staff record.")

    existing_work_email = StaffModel.query.filter_by(work_email=work_email).first()
    if existing_work_email and existing_work_email.user_id != exclude_user_id:
        abort(400, message="Work email already exists for another staff record.")


def _create_staff_for_user(user: UserModel, user_data: dict | None = None):
    user_data = user_data or {}
    default_first_name = user.username[:30]
    default_last_name = "Staff"
    default_position = "Staff"

    work_phone = user_data.get("work_phone") or f"0207{user.id:07d}"
    mobile_phone = user_data.get("mobile_phone") or f"07123{user.id:06d}"
    work_email = user_data.get("work_email") or _staff_work_email(user.username, user.id)

    _validate_staff_unique_fields(work_phone, mobile_phone, work_email)

    staff = StaffModel(
        first_name=(user_data.get("first_name") or default_first_name)[:30],
        last_name=(user_data.get("last_name") or default_last_name)[:30],
        date_of_birth=user_data.get("date_of_birth") or date(1970, 1, 1),
        work_phone=work_phone,
        mobile_phone=mobile_phone,
        work_email=work_email,
        position=(user_data.get("position") or default_position)[:50],
        user_id=user.id,
    )
    db.session.add(staff)


def _sync_staff_for_user(user: UserModel, user_data: dict | None = None):
    user_data = user_data or {}

    if not user.staff:
        _create_staff_for_user(user, user_data)
        return

    updated_work_phone = user_data.get("work_phone") or user.staff.work_phone
    updated_mobile_phone = user_data.get("mobile_phone") or user.staff.mobile_phone
    updated_work_email = user_data.get("work_email") or user.staff.work_email
    if user_data.get("work_email") is None and user_data.get("username") is not None:
        updated_work_email = _staff_work_email(user.username, user.id)

    _validate_staff_unique_fields(
        updated_work_phone,
        updated_mobile_phone,
        updated_work_email,
        exclude_user_id=user.id,
    )

    if user_data.get("first_name") is not None:
        user.staff.first_name = user_data["first_name"][:30]
    elif user_data.get("username") is not None:
        user.staff.first_name = user.username[:30]

    if user_data.get("last_name") is not None:
        user.staff.last_name = user_data["last_name"][:30]
    if user_data.get("date_of_birth") is not None:
        user.staff.date_of_birth = user_data["date_of_birth"]
    if user_data.get("work_phone") is not None:
        user.staff.work_phone = user_data["work_phone"]
    if user_data.get("mobile_phone") is not None:
        user.staff.mobile_phone = user_data["mobile_phone"]
    if user_data.get("work_email") is not None:
        user.staff.work_email = user_data["work_email"]
    elif user_data.get("username") is not None:
        user.staff.work_email = _staff_work_email(user.username, user.id)
    if user_data.get("position") is not None:
        user.staff.position = user_data["position"][:50]


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserCreateSchema)
    def post(self, user_data):
        if UserModel.find_by_username(user_data["username"]):
            abort(400, message="A user with that username already exists.")

        user = UserModel()
        user.username=user_data["username"]
        user.password=pbkdf2_sha256.hash(user_data["password"])

        db.session.add(user)
        db.session.flush()
        _create_staff_for_user(user, user_data)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Staff record contains duplicate unique fields (phone or email).")

        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserCreateSchema)
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


@blp.route("/me")
class UserMe(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        current_user_id = get_jwt_identity()
        try:
            user_id = int(current_user_id)
        except (TypeError, ValueError):
            abort(401, message="Invalid user identity in token.")

        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")
        return user


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
    @blp.arguments(UserUpdateSchema)
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

        _sync_staff_for_user(user, user_data)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Staff update conflicts with existing unique fields (phone or email).")

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
