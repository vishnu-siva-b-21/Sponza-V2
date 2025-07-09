from sponza_app import db
from flask_jwt_extended import (
    get_jwt,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from flask import jsonify, request
from functools import wraps
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import date, datetime, timezone
import uuid
import base64
from random import randint


def role_required(required_roles):
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("role")
                current_user = get_jwt_identity()
                if user_role not in required_roles:
                    return (
                        jsonify(
                            {
                                "message": "You are not authorized to access this resource.",
                                "status": "error",
                            }
                        ),
                        403,
                    )
                return func(*args, **kwargs)
            except Exception as e:
                print(str(e))
                return (
                    jsonify(
                        {
                            "message": str(e),
                            "status": "error",
                            "error": str(e),
                        }
                    ),
                    401,
                )

        return wrapper

    return decorator


def create_id():
    uuid_val = uuid.uuid4()
    b64_uuid = base64.urlsafe_b64encode(uuid_val.bytes).rstrip(b"=")
    return b64_uuid[:4].decode("utf-8")


class Sponsor(db.Model):
    __tablename__ = "sponsors"

    sponsor_id = db.Column(
        db.String(200),
        primary_key=True,
        default=lambda: f"@SF-{create_id()}-{randint(1, 10000)}",
    )
    sponsor_company_name = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    sponsor_profile_image = db.Column(
        db.String(40), nullable=False, default="sponsor.png"
    )
    industry = db.Column(db.String(40), nullable=False)
    admin_approved = db.Column(db.String(20), nullable=False, default="False")
    admin_flag = db.Column(db.String(20), nullable=False, default="False")
    admin_flag_time = db.Column(db.DateTime, nullable=True)

    campaigns = db.relationship("Campaign", backref="owner", lazy=True)

    def get_id(self):
        return self.sponsor_id

    def __repr__(self):
        return f"Sponsor({self.sponsor_company_name})"

    def get_reset_token(self):
        serializer_object = Serializer(
            current_app.config["SECRET_KEY"], salt="email-verification"
        )
        return serializer_object.dumps({"sponsor_id": self.sponsor_id})

    @staticmethod
    def verify_reset_token(token, expires_sec=600):
        serializer_object = Serializer(
            current_app.config["SECRET_KEY"], salt="email-verification"
        )
        try:
            sponsor_id = serializer_object.loads(token, max_age=expires_sec)[
                "sponsor_id"
            ]
        except:
            return None

        user = Sponsor.query.get(sponsor_id)
        if user is None:
            return None

        return user


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(
        db.String(200),
        primary_key=True,
        default=lambda: f"@AD-{create_id()}-{randint(1, 100)}",
    )
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Admin({self.email})"


class CampaignInfluencer(db.Model):
    __tablename__ = "campaign_influencers"

    ci_id = db.Column(
        db.String(200),
        primary_key=True,
        default=lambda: f"@CI-{create_id()}-{randint(1, 10000)}",
    )
    campaign_id = db.Column(
        db.String(200), db.ForeignKey("campaigns.campaign_id"), nullable=False
    )
    influencer_id = db.Column(
        db.String(200), db.ForeignKey("influencers.influencer_id"), nullable=False
    )
    status = db.Column(db.String(20), nullable=False)
    campaign_amt = db.Column(db.Integer, nullable=False, default=0)

    campaign = db.relationship("Campaign", back_populates="campaign_influencers")
    influencer = db.relationship("Influencer", back_populates="campaign_influencers")

    def get_id(self):
        return self.ci_id

    def __repr__(self):
        return f"CampaignInfluencer(Campaign: {self.campaign_id}, Influencer: {self.influencer_id}, Status: {self.status})"


class Influencer(db.Model):
    __tablename__ = "influencers"

    influencer_id = db.Column(
        db.String(200),
        primary_key=True,
        default=lambda: f"@IN-{create_id()}-{randint(1, 100)}",
    )
    email = db.Column(db.String(40), unique=True, nullable=False)
    influencer_user_name = db.Column(db.String(40), unique=False, nullable=False)
    influencer_niche = db.Column(db.String(40), unique=False, nullable=False)
    influencer_social_media_platform = db.Column(
        db.String(40), unique=False, nullable=False
    )
    influencer_social_media_link = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    influencer_profile_image = db.Column(
        db.String(40), nullable=False, default="influencer.png"
    )
    influencer_income = db.Column(db.Integer, nullable=False, default=0)
    admin_flag = db.Column(db.String(20), nullable=False, default="False")
    admin_flag_time = db.Column(db.DateTime, nullable=True)

    campaigns = db.relationship(
        "Campaign",
        secondary="campaign_influencers",
        back_populates="influencers",
        overlaps="campaign_influencers,influencer",
    )

    campaign_influencers = db.relationship(
        "CampaignInfluencer", back_populates="influencer", overlaps="campaign"
    )

    def get_id(self):
        return self.influencer_id

    def __repr__(self):
        return f"Influencer({self.influencer_user_name})"

    def get_reset_token(self):
        serializer_object = Serializer(
            current_app.config["SECRET_KEY"], salt="email-verification"
        )
        return serializer_object.dumps({"influencer_id": self.influencer_id})

    @staticmethod
    def verify_reset_token(token, expires_sec=600):
        serializer_object = Serializer(
            current_app.config["SECRET_KEY"], salt="email-verification"
        )
        try:
            influencer_id = serializer_object.loads(token, max_age=expires_sec)[
                "influencer_id"
            ]
        except:
            return None

        user = Influencer.query.get(influencer_id)
        if user is None:
            return None

        return user


class Campaign(db.Model):
    __tablename__ = "campaigns"

    campaign_id = db.Column(
        db.String(200),
        primary_key=True,
        default=lambda: f"@CP-{create_id()}-{randint(1, 10000)}",
    )
    campaign_title = db.Column(db.String, nullable=False, unique=True)
    campaign_desc = db.Column(db.String, nullable=False)
    campaign_profile_image = db.Column(
        db.String(40), nullable=False, default="campaign.png"
    )
    campaign_start_date = db.Column(db.Date, default=date.today)
    campaign_end_date = db.Column(db.Date, nullable=False)
    campaign_expenses = db.Column(db.Integer, nullable=False, default=0)
    campaign_visibility = db.Column(db.String(20), nullable=False)
    campaign_goals = db.Column(db.String, nullable=False)
    admin_flag = db.Column(db.String(20), nullable=False, default="False")
    admin_flag_time = db.Column(db.DateTime, nullable=True)

    sponsor_id = db.Column(
        db.String(200), db.ForeignKey("sponsors.sponsor_id"), nullable=False
    )

    influencers = db.relationship(
        "Influencer",
        secondary="campaign_influencers",
        back_populates="campaigns",
        overlaps="campaign_influencers,influencer",
    )

    campaign_influencers = db.relationship(
        "CampaignInfluencer", back_populates="campaign", overlaps="influencer"
    )

    def __repr__(self):
        return f"Campaign({self.campaign_title})"
