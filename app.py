from datetime import timedelta
from http import HTTPStatus
import secrets
from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from models import db
from blocklist import BLOCKLIST

from resources.user import blp as UserBlueprint
from resources.patient import blp as PatientBlueprint


app = Flask(__name__)
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

# Access token lifetime
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)  # or hours=1, etc.
# Refresh token lifetime
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
db.init_app(app)
api = Api(app)

"""
JWT related configuration. The following functions includes:
1) add claims to each jwt
2) customize the token expired error message
"""
app.config["JWT_SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
jwt = JWTManager(app)

"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below
"""


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    # TODO: Read from a config file instead of hard-coding
    # Identity is stored as a string in the JWT; treat user with id 1 as admin
    try:
        is_admin = int(identity) == 1
    except (TypeError, ValueError):
        is_admin = False
    return {"is_admin": is_admin}


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    print("INVALID TOKEN, REASON:", error)
    print("VERIFY SECRET:", app.config["JWT_SECRET_KEY"])
    print("AUTH HEADER:", request.headers.get("Authorization"))
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        HTTPStatus.UNAUTHORIZED,
    )


# JWT configuration ends


with app.app_context():
    import models  # noqa: F401

    db.create_all()


api.register_blueprint(UserBlueprint)
api.register_blueprint(PatientBlueprint)