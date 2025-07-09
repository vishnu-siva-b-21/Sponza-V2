from flask import (
    Blueprint,
    request,
    jsonify,
    session,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)
from sponza_app.models import Influencer, Sponsor, Admin
from sponza_app import db, bcrypt
from sponza_app.modules.main.utils import send_mail

main = Blueprint("main", __name__)


@main.route("/check-auth", methods=["GET"])
@jwt_required()
def check_auth():
    try:
        jwt_data = get_jwt()
        role = jwt_data.get("role")
        if role == "sponsor":
            redirect_url = "/spn/dashboard"
        elif role == "influencer":
            redirect_url = "/inf/dashboard"
        elif role == "admin":
            redirect_url = "/admin/dashboard"
        else:
            return (
                jsonify({"status": "unauthenticated", "message": "Invalid role"}),
                403,
            )

        return jsonify({"status": "authenticated", "redirect_url": redirect_url}), 200
    except Exception as e:
        return jsonify({"status": "unauthenticated", "message": str(e)}), 401


@main.route("/login", methods=["POST"])
def user_login():
    data = request.get_json()
    email = data.get("email", "").strip()
    role = data.get("role")
    password = data.get("password", "").strip()
    remember_me = data.get("rememberMe", False)

    session["user_login_email"] = email
    session["user_role"] = role

    if role == "sponsor":
        user = Sponsor.query.filter_by(email=email).first()
    elif role == "influencer":
        user = Influencer.query.filter_by(email=email).first()
    elif role == "admin":
        user = Admin.query.filter_by(email=email).first()
    else:
        return jsonify({"message": "Invalid role selected!", "status": "warning"}), 400
    if role != "admin" and user and user.admin_flag == "True":
        return (
            jsonify(
                {
                    "message": "Your account has been temporarily blocked. Please check your email for more details.",
                    "status": "warning",
                }
            ),
            403,
        )

    if role == "sponsor" and user and user.admin_approved != "True":
        return (
            jsonify(
                {
                    "message": "Your account has not been approved by the admin. Please wait till your account is approved, after approval you will recieve email.",
                    "status": "warning",
                }
            ),
            403,
        )

    if user:
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(
                identity=user.email, additional_claims={"role": role}
            )
            refresh_token = create_refresh_token(
                identity=user.email, additional_claims={"role": role}
            )
            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "status": "success",
                        "tokens": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "message": "Invalid password. Please try again.",
                        "status": "error",
                    }
                ),
                401,
            )
    else:
        return (
            jsonify(
                {"message": "Email not found. Please try again.", "status": "error"}
            ),
            404,
        )


@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    role = data.get("role", "")
    if role == "sponsor":
        spn_company = data.get("spn_company", "").strip()
        spn_email = data.get("spn_email", "").strip()
        spn_industry = data.get("spn_industry", "").strip()
        spn_password = data.get("spn_password", "").strip()
        existing_user = Sponsor.query.filter_by(email=spn_email).first()
        if existing_user is None:
            hashed_password = bcrypt.generate_password_hash(spn_password).decode(
                "utf-8"
            )
            sponsor = Sponsor(
                sponsor_company_name=spn_company,
                email=spn_email,
                industry=spn_industry,
                password=hashed_password,
            )
            db.session.add(sponsor)
            db.session.commit()
            return jsonify(
                {
                    "message": "Request redirected to Admin, Wait for the Mail.",
                    "status": "success",
                }
            )
        else:
            return jsonify(
                {
                    "message": "Sponsor already exists, Please use a different email.",
                    "status": "error",
                }
            )
    elif role == "influencer":
        inf_uname = data.get("inf_uname", "").strip()
        inf_email = data.get("inf_email", "").strip()
        inf_niche = data.get("inf_niche", "").strip()
        inf_password = data.get("inf_password", "").strip()
        inf_platform = data.get("inf_platform", "").strip()
        inf_platform_link = data.get("inf_platform_link", "").strip()
        existing_user = Influencer.query.filter_by(email=inf_email).first()
        if existing_user is None:
            hashed_password = bcrypt.generate_password_hash(inf_password).decode(
                "utf-8"
            )
            influencer = Influencer(
                influencer_user_name=inf_uname,
                email=inf_email,
                influencer_niche=inf_niche,
                influencer_social_media_platform=inf_platform,
                influencer_social_media_link=inf_platform_link,
                password=hashed_password,
            )
            db.session.add(influencer)
            db.session.commit()
            return jsonify(
                {
                    "message": "Influencer added successfully",
                    "status": "success",
                }
            )
        else:
            return jsonify(
                {
                    "message": "Influencer already exists, Please use a different email.",
                    "status": "error",
                }
            )
    else:
        return jsonify(
            {
                "message": "Invalid role.",
                "status": "error",
            }
        )


@main.route("/logout", methods=["POST"])
@jwt_required()
def user_logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@main.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    user_role = get_jwt().get("role")
    new_access_token = create_access_token(
        identity=current_user, additional_claims={"role": user_role}
    )
    return jsonify(access_token=new_access_token), 200


@main.route("/user-reset-request", methods=["POST"])
def user_reset_request():
    if request.method == "POST":
        data = request.json
        email = data.get("email")
        role = data.get("role")
        if role == "influencer":
            user = Influencer.query.filter_by(email=email).first()
        elif role == "sponsor":
            user = Sponsor.query.filter_by(email=email).first()
        if user:
            send_mail(user, user.get_reset_token(), role)
            return (
                jsonify(
                    {
                        "message": "An email has been sent with the instructions to reset your password"
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Invalid Data or Email not registred!"})


@main.route("/user-reset-password/<role>/<token>", methods=["POST"])
def user_reset_password(role, token):
    user = (
        Influencer.verify_reset_token(token)
        if role == "influencer"
        else Sponsor.verify_reset_token(token)
    )

    if user is None:
        return jsonify({"success": False, "message": "Invalid or expired token"})

    data = request.get_json()
    if not data or not data.get("password"):
        return jsonify({"success": False, "message": "Password is required"})

    hashed_password = bcrypt.generate_password_hash(data["password"].strip()).decode(
        "utf-8"
    )
    user.password = hashed_password
    db.session.commit()

    return jsonify({"success": True, "message": "Password updated successfully"})


@main.route("/get-all-users/<role>", methods=["GET"])
def get_all_users(role):
    if role == "sponsor":
        users = Sponsor.query.all()
    elif role == "influencer":
        users = Influencer.query.all()
    else:
        return {"error": "role not found"}, 404
    user_list = [user.email for user in users]
    return jsonify(user_list)


@main.route("/db-drop-all", methods=["DELETE"])
def db_drop_all():
    db.drop_all()
    return jsonify(message="Dropped all the database")
