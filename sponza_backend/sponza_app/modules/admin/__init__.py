from flask import (
    Blueprint,
    request,
    jsonify,
)
from flask_jwt_extended import get_jwt, get_jwt_identity
from sponza_app.models import (
    Campaign,
    CampaignInfluencer,
    Influencer,
    Sponsor,
    role_required,
)
from sponza_app import db
from sponza_app.modules.admin.utils import (
    return_sponsor_profile_image,
    return_inf_profile_image,
    return_campaign_image,
    send_flag_mail,
    send_camp_flag_mail,
    send_approve_mail,
    send_reject_mail,
)

from datetime import date, datetime

admin = Blueprint("admin", __name__)


@admin.route("/api/dashboard")
@role_required("admin")
def api_admin_dashboard():
    total_infs = len(Influencer.query.all())
    total_spns = len(Sponsor.query.all())
    total_users = total_infs + total_spns
    total_expense = sum(ci.campaign_amt for ci in CampaignInfluencer.query.all())
    campaigns = []
    for camp in Campaign.query.filter_by(admin_flag="True").all():
        total_camp_days = (camp.campaign_end_date - camp.campaign_start_date).days
        completed_camp_days = (date.today() - camp.campaign_start_date).days
        progress = (
            int((completed_camp_days / total_camp_days) * 100)
            if total_camp_days > 0
            else 0
        )
        accepted_influencers = CampaignInfluencer.query.filter_by(
            campaign_id=camp.campaign_id, status="accepted"
        ).all()
        campaigns.append(
            {
                "role": "campaign",
                "campaign_id": camp.campaign_id,
                "campaign_title": camp.campaign_title,
                "campaign_profile_image": "http://127.0.0.1:5000/"
                + return_campaign_image(camp.campaign_profile_image),
                "sponsor_name": Sponsor.query.get(camp.sponsor_id).sponsor_company_name,
                "total_camp_days": total_camp_days,
                "completed_camp_days": completed_camp_days,
                "progress": progress,
                "all_influencers": [
                    inf.influencer.influencer_user_name for inf in accepted_influencers
                ],
            }
        )
    sponsors = []
    for spn in Sponsor.query.filter_by(admin_flag="True").all():
        sponsors.append(
            {
                "role": "sponsor",
                "sponsor_id": spn.sponsor_id,
                "industry": spn.industry,
                "sponsor_company_name": spn.sponsor_company_name,
                "sponsor_profile_image": "http://127.0.0.1:5000/"
                + return_sponsor_profile_image(spn.sponsor_profile_image),
                "campaign_titles": [camp.campaign_title for camp in spn.campaigns],
            }
        )
    unapproved_sponsors = []
    for spn in Sponsor.query.filter_by(admin_approved="False").all():
        unapproved_sponsors.append(
            {
                "role": "sponsor",
                "sponsor_id": spn.sponsor_id,
                "industry": spn.industry,
                "sponsor_company_name": spn.sponsor_company_name,
                "sponsor_profile_image": "http://127.0.0.1:5000/"
                + return_sponsor_profile_image(spn.sponsor_profile_image),
                "campaign_titles": [camp.campaign_title for camp in spn.campaigns],
            }
        )
    influencers = []
    for inf in Influencer.query.filter_by(admin_flag="True").all():
        influencers.append(
            {
                "role": "influencer",
                "influencer_id": inf.influencer_id,
                "influencer_user_name": inf.influencer_user_name,
                "influencer_niche": inf.influencer_niche,
                "influencer_social_media_link": inf.influencer_social_media_link,
                "influencer_social_media_platform": inf.influencer_social_media_platform,
                "influencer_profile_image": "http://127.0.0.1:5000/"
                + return_inf_profile_image(inf.influencer_profile_image),
                "campaign_titles": [
                    camp.campaign_title
                    for camp in Campaign.query.join(CampaignInfluencer)
                    .filter(
                        CampaignInfluencer.influencer_id == inf.influencer_id,
                        CampaignInfluencer.status == "accepted",
                    )
                    .all()
                ],
            }
        )
    response = {
        "total_infs": total_infs,
        "total_spns": total_spns,
        "total_users": total_users,
        "total_expense": total_expense,
        "campaigns": campaigns,
        "influencers": influencers,
        "sponsors": sponsors,
        "unapproved_sponsors": unapproved_sponsors,
    }
    return jsonify(response)


@admin.route("/api/find")
@role_required("admin")
def admin_find_api():
    campaigns = Campaign.query.filter_by(admin_flag="False").all()
    influencers = Influencer.query.filter_by(admin_flag="False").all()
    sponsors = Sponsor.query.filter_by(admin_flag="False").all()

    def serialize_campaign(camp):
        total_camp_days = (camp.campaign_end_date - camp.campaign_start_date).days
        completed_camp_days = (date.today() - camp.campaign_start_date).days
        progress = (
            int((completed_camp_days / total_camp_days) * 100)
            if total_camp_days > 0
            else 0
        )
        return {
            "campaign_id": camp.campaign_id,
            "campaign_title": camp.campaign_title,
            "campaign_profile_image": "http://127.0.0.1:5000/"
            + return_campaign_image(camp.campaign_profile_image),
            "sponsor_name": Sponsor.query.get(camp.sponsor_id).sponsor_company_name,
            "total_camp_days": total_camp_days,
            "completed_camp_days": completed_camp_days,
            "progress": progress,
            "all_influencers": [
                inf.influencer.influencer_user_name
                for inf in CampaignInfluencer.query.filter_by(
                    campaign_id=camp.campaign_id, status="accepted"
                ).all()
            ],
        }

    def serialize_sponsor(spn):
        return {
            "sponsor_id": spn.sponsor_id,
            "email": spn.email,
            "sponsor_company_name": spn.sponsor_company_name,
            "sponsor_profile_image": "http://127.0.0.1:5000/"
            + return_sponsor_profile_image(spn.sponsor_profile_image),
            "campaign_titles": [camp.campaign_title for camp in spn.campaigns],
        }

    def serialize_influencer(inf):
        return {
            "influencer_id": inf.influencer_id,
            "influencer_user_name": inf.influencer_user_name,
            "influencer_niche": inf.influencer_niche,
            "influencer_income": inf.influencer_income,
            "influencer_social_media_platform": inf.influencer_social_media_platform,
            "influencer_social_media_link": inf.influencer_social_media_link,
            "influencer_profile_image": "http://127.0.0.1:5000/"
            + return_inf_profile_image(inf.influencer_profile_image),
            "campaign_titles": [
                camp.campaign_title
                for camp in Campaign.query.join(CampaignInfluencer)
                .filter(
                    CampaignInfluencer.influencer_id == inf.influencer_id,
                    CampaignInfluencer.status == "accepted",
                )
                .all()
            ],
        }

    data = {
        "campaigns": [serialize_campaign(camp) for camp in campaigns],
        "sponsors": [serialize_sponsor(spn) for spn in sponsors],
        "influencers": [serialize_influencer(inf) for inf in influencers],
    }
    return jsonify(data)


@admin.route("/get-data")
@role_required("admin")
def get_data():
    data = {"msg": "Hello World", "role": get_jwt().get("role")}
    return jsonify(data)


@admin.route("/get-graph-data")
@role_required("admin")
def get_graph_data():
    campaigns = Campaign.query.all()
    if not campaigns:
        return jsonify({"error": "No campaigns found"}), 404
    data = {camp.campaign_title: camp.campaign_expenses for camp in campaigns}
    return jsonify(data)


@admin.route("/get-pie-data")
@role_required("admin")
def get_pie_data():
    inf_count = len(Influencer.query.all())
    camp_count = len(Campaign.query.all())
    data = {"campaign": camp_count, "influencer": inf_count}
    return jsonify(data)


@admin.route("/flag", methods=["PUT"])
@role_required("admin")
def flag():
    data = request.json
    role = data.get("role")
    id = data.get("id")
    if role == "camp":
        camp = Campaign.query.get(id)
        camp.admin_flag = "True"
        camp.admin_flag_time = datetime.now()
        send_camp_flag_mail.delay(Sponsor.query.get(camp.sponsor_id).email, camp.campaign_title)
        camp_inf = CampaignInfluencer.query.filter(
            CampaignInfluencer.campaign_id == camp.campaign_id,
            CampaignInfluencer.status != "accepted",
        ).all()
        for camp in camp_inf:
            db.session.delete(camp)
        db.session.commit()
    elif role == "inf":
        inf = Influencer.query.get(id)
        inf.admin_flag_time = datetime.now()
        inf.admin_flag = "True"
        send_flag_mail.delay(inf.email, "Influencer")
    elif role == "spn":
        spn = Sponsor.query.get(id)
        spn.admin_flag_time = datetime.now()
        spn.admin_flag = "True"
        send_flag_mail.delay(spn.email, "Sponsor")
    else:
        return jsonify({"error": "Invaild Data! Data not Found"}), 404
    db.session.commit()
    return (
        jsonify({"message": "Flag Successful!"}),
        200,
    )


@admin.route("/approve", methods=["PUT"])
@role_required("admin")
def approve():
    data = request.json
    role = data.get("role")
    id = data.get("id")
    if role == "sponsor":
        spn = Sponsor.query.get(id)
        spn.admin_approved = "True"
        send_approve_mail.delay(spn.email, "Sponsor")
    else:
        return jsonify({"error": "Invaild Data! Data not Found"}), 404
    db.session.commit()
    return (
        jsonify({"message": "Successfully Approved!"}),
        200,
    )


@admin.route("/reject", methods=["DELETE"])
@role_required("admin")
def reject():
    data = request.json
    print(data)
    role = data.get("role")
    id = data.get("id")
    if role == "sponsor":
        spn = Sponsor.query.get(id)
        send_reject_mail.delay(spn.email, "Sponsor")
        db.session.delete(spn)
    else:
        return jsonify({"error": "Invaild Data! Data not Found"}), 404
    db.session.commit()
    return (
        jsonify({"message": "Successfully Rejected"}),
        200,
    )


@admin.route("/unflag", methods=["PUT"])
@role_required("admin")
def unflag():
    data = request.json
    role = data.get("role")
    id = data.get("id")
    if role == "campaign":
        camp = Campaign.query.get(id)
        camp.admin_flag = "False"
        camp.admin_flag_time = None
    elif role == "influencer":
        inf = Influencer.query.get(id)
        inf.admin_flag = "False"
        inf.admin_flag_time = None
    elif role == "sponsor":
        spn = Sponsor.query.get(id)
        spn.admin_flag = "False"
        spn.admin_flag_time = None
    else:
        return jsonify({"error": "Invaild Data! Data not Found"}), 404
    db.session.commit()
    return (
        jsonify({"message": "Unflag Successful!"}),
        200,
    )
