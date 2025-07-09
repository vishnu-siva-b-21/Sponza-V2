from flask import (
    Blueprint,
    request,
    jsonify,
)
from flask_jwt_extended import get_jwt_identity
from sponza_app.models import (
    Influencer,
    Campaign,
    Sponsor,
    CampaignInfluencer,
    role_required,
)
from sponza_app import db, cache
from sponza_app.modules.influencer.utils import (
    del_save_image,
    return_profile_image,
    return_campaign_image,
    del_inf_image,
    send_negotiate_mail,
)
from datetime import date


influencer = Blueprint("influencer", __name__)


@influencer.route("/base")
@cache.cached(timeout=50)
@role_required("influencer")
def influencer_base():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    image = "http://127.0.0.1:5000/" + return_profile_image(
        current_user.influencer_profile_image
    )
    return jsonify(
        {
            "influencer": {
                "name": current_user.influencer_user_name,
                "image": image,
            }
        }
    )


@influencer.route("/api/dashboard")
@role_required("influencer")
def influencer_dashboard_api():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    image = "http://127.0.0.1:5000/" + return_profile_image(
        current_user.influencer_profile_image
    )
    accepted_camp = []

    for camp_inf in CampaignInfluencer.query.filter_by(
        influencer_id=current_user.influencer_id, status="accepted"
    ).all():
        camp = camp_inf.campaign
        total_camp_days = (camp.campaign_end_date - camp.campaign_start_date).days
        completed_camp_days = (date.today() - camp.campaign_start_date).days
        progress = (
            int((completed_camp_days / total_camp_days) * 100)
            if total_camp_days > 0
            else 0
        )

        inf_data = {
            "id": camp.campaign_id,
            "title": camp.campaign_title,
            "sponsor": Sponsor.query.get(camp.sponsor_id).sponsor_company_name,
            "progress": progress,
            "desc": camp.campaign_desc,
            "goals": camp.campaign_goals,
            "end_date": camp.campaign_end_date,
            "image": "http://127.0.0.1:5000/"
            + return_campaign_image(camp.campaign_profile_image),
            "camp_amt": camp_inf.campaign_amt,
            "flag": camp.admin_flag,
        }
        accepted_camp.append(inf_data)

    pending_requests_count = CampaignInfluencer.query.filter_by(
        influencer_id=current_user.influencer_id, status="camp_sent_pending"
    ).count()

    num_total_camp = Campaign.query.count()

    return jsonify(
        {
            "influencer": {
                "name": current_user.influencer_user_name,
                "id": current_user.influencer_id,
                "income": current_user.influencer_income,
                "image": image,
            },
            "campaigns": accepted_camp,
            "num_total_camp": num_total_camp,
            "pending_requests_count": pending_requests_count,
        }
    )


@influencer.route("/api/campaigns")
@role_required("influencer")
def influencer_api_campaigns():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()
    sponsor_name = ""

    if request.args.get("id"):
        sponsor_id = request.args.get("id")
        all_camp = Campaign.query.filter_by(
            sponsor_id=sponsor_id, admin_flag="False", campaign_visibility="public"
        ).all()
        sponsor_name = Sponsor.query.get(sponsor_id).sponsor_company_name
    else:
        all_camp = Campaign.query.filter_by(
            admin_flag="False", campaign_visibility="public"
        ).all()
    serialized_campaigns = []
    for camp in all_camp:
        serialized_campaigns.append(
            {
                "campaign_id": camp.campaign_id,
                "campaign_profile_image": "http://127.0.0.1:5000/"
                + return_campaign_image(camp.campaign_profile_image),
                "campaign_title": camp.campaign_title,
                "campaign_goals": camp.campaign_goals,
                "campaign_desc": camp.campaign_desc,
                "campaign_end_date": camp.campaign_end_date.strftime("%Y-%m-%d"),
                "sponsor_id": camp.sponsor_id,
                "sponser_name": Sponsor.query.get(camp.sponsor_id).sponsor_company_name,
            }
        )

    inf_camp = CampaignInfluencer.query.filter_by(
        influencer_id=current_user.influencer_id
    ).all()

    inf_camp_ids = [camp_inf.campaign_id for camp_inf in inf_camp]
    non_inf_camp = [
        camp for camp in serialized_campaigns if camp["campaign_id"] not in inf_camp_ids
    ]

    return jsonify(
        {
            "influencer_name": current_user.influencer_user_name,
            "influencer_id": current_user.influencer_id,
            "all_camp": non_inf_camp,
            "sponsor_name": sponsor_name,
        }
    )


@influencer.route("/api/requests")
@role_required("influencer")
def influencer_api_requests():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()

    inf_sent_pending = []
    camp_sent_pending = []

    # Serialize the 'inf_sent_pending' list
    for camp in CampaignInfluencer.query.filter_by(
        influencer_id=current_user.influencer_id, status="inf_sent_pending"
    ).all():
        camp_data = {
            "main_id": camp.ci_id,
            "id": camp.campaign.campaign_id,
            "title": camp.campaign.campaign_title,
            "sponsor": Sponsor.query.get(camp.campaign.sponsor_id).sponsor_company_name,
            "image": "http://127.0.0.1:5000/"
            + return_campaign_image(camp.campaign.campaign_profile_image),
            "camp_pay": camp.campaign_amt,
        }
        inf_sent_pending.append(camp_data)

    # Serialize the 'camp_sent_pending' list
    for camp in CampaignInfluencer.query.filter_by(
        influencer_id=current_user.influencer_id, status="camp_sent_pending"
    ).all():
        camp_data = {
            "main_id": camp.ci_id,
            "id": camp.campaign.campaign_id,
            "title": camp.campaign.campaign_title,
            "desc": camp.campaign.campaign_desc,
            "end_date": camp.campaign.campaign_end_date,
            "sponsor_company_name": Sponsor.query.get(
                camp.campaign.sponsor_id
            ).sponsor_company_name,
            "camp_amt": camp.campaign_amt,
            "image": "http://127.0.0.1:5000/"
            + return_campaign_image(camp.campaign.campaign_profile_image),
            "camp_pay": camp.campaign_amt,
        }
        camp_sent_pending.append(camp_data)

    # Now serialize both lists properly
    serialized_inf_sent_pending = inf_sent_pending
    serialized_camp_sent_pending = camp_sent_pending

    return jsonify(
        influencer_id=current_user.influencer_id,
        inf_sent_pending=serialized_inf_sent_pending,
        camp_sent_pending=serialized_camp_sent_pending,
    )


@influencer.route("/profile")
@role_required("influencer")
def influencer_profile():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()
    influencer_details = {}
    influencer_details["influencer_id"] = current_user.influencer_id
    influencer_details["influencer_user_name"] = current_user.influencer_user_name
    influencer_details["email"] = current_user.email
    influencer_details["influencer_niche"] = current_user.influencer_niche
    influencer_details["influencer_income"] = current_user.influencer_income
    influencer_details["influencer_social_media_platform"] = (
        current_user.influencer_social_media_platform
    )
    influencer_details["influencer_social_media_link"] = (
        current_user.influencer_social_media_link
    )

    influencer_details["image"] = "http://127.0.0.1:5000/" + return_profile_image(
        current_user.influencer_profile_image
    )
    return jsonify(
        influencer_details,
    )


@influencer.route("/update-profile", methods=["PUT"])
@role_required("influencer")
def update_profile():
    try:
        user_email = get_jwt_identity()
        current_user = Influencer.query.filter_by(email=user_email).first()
        if not current_user:
            return jsonify({"success": False, "message": "User not found"}), 404

        file_name = current_user.influencer_profile_image
        if "profile_pic" in request.files:
            profile_pic = request.files["profile_pic"]
            file_name = del_save_image(
                profile_pic,
                current_user.influencer_profile_image,
                "influencer",
            )
        Influencer.query.filter_by(email=user_email).update(
            dict(
                influencer_user_name=request.form.get("influencer_user_name").strip(),
                email=request.form.get("email").strip(),
                influencer_profile_image=file_name,
                influencer_social_media_platform=request.form.get(
                    "influencer_social_media_platform"
                ),
                influencer_social_media_link=request.form.get(
                    "influencer_social_media_link"
                ),
            )
        )
        db.session.commit()
        return jsonify({"success": True, "message": "Profile updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": "Internal Server Error"}), 500


@influencer.route("/send-ad-request/<camp_id>", methods=["POST"])
@role_required("influencer")
def send_ad_request(camp_id):
    ad_data = request.json
    inf_id = ad_data["adInfluencerid"]
    camp_pay = ad_data["adPayment"]

    campaign = Campaign.query.get(camp_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    influencer = Influencer.query.get(inf_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    camp_inf = CampaignInfluencer.query.filter_by(
        campaign_id=campaign.campaign_id, influencer_id=influencer.influencer_id
    ).first()
    if camp_inf:
        if camp_inf.status == "inf_sent_pending":
            return jsonify({"error": "Ad request already sent"}), 409
        elif camp_inf.status == "camp_sent_pending":
            return jsonify({"error": "Ad request already recieved"}), 409
        elif camp_inf.status == "accepted":
            return jsonify({"error": "Ad request already accepted"}), 409
        else:
            return jsonify({"error": "Error"}), 404

    campaign_influencer = CampaignInfluencer(
        campaign_id=campaign.campaign_id,
        influencer_id=influencer.influencer_id,
        campaign_amt=int(camp_pay),
        status="inf_sent_pending",
    )

    db.session.add(campaign_influencer)
    db.session.commit()

    return jsonify({"message": "Ad request sent successfully"}), 200


@influencer.route("/negotiate/<id>", methods=["POST"])
@role_required("influencer")
def negotiate(id):
    camp_inf = CampaignInfluencer.query.get(id)
    if not camp_inf:
        return jsonify({"message": "Request not found", "status": "error"}), 404

    negotiate_amt = request.json.get("negotiate-amt").strip()
    updated = False

    if negotiate_amt:
        if negotiate_amt and int(negotiate_amt) != camp_inf.campaign_amt:
            camp_inf.campaign_amt = int(negotiate_amt)
            camp_inf.status = "inf_sent_pending"
            influencer_name = Influencer.query.get(
                camp_inf.influencer_id
            ).influencer_user_name
            campaign = Campaign.query.get(camp_inf.campaign_id)
            sponsor = Sponsor.query.get(campaign.sponsor_id)
            send_negotiate_mail(
                sponsor.email,
                "sponsor",
                influencer_name,
                campaign.campaign_title,
                negotiate_amt,
            )
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Changed Negotiate Amount Successfully",
                        "status": "success",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "message": "No change detected for Negotiate Amount",
                        "status": "error",
                    }
                ),
                400,
            )
    else:
        return jsonify({"message": "Invalid salary input", "status": "error"}), 400


@influencer.route("/accept-ad-req", methods=["PUT"])
@role_required("influencer")
def accept_ad_req():
    data = request.json
    inf_id = data.get("inf_id")
    camp_id = data.get("camp_id")

    campaign = Campaign.query.get(camp_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    influencer = Influencer.query.get(inf_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    camp_inf = CampaignInfluencer.query.filter_by(
        campaign_id=campaign.campaign_id, influencer_id=influencer.influencer_id
    ).first()

    if camp_inf:
        if camp_inf.status == "accepted":
            return jsonify({"error": "Request has already been accepted"}), 400

        camp_inf.status = "accepted"

        campaign.campaign_expenses += camp_inf.campaign_amt
        influencer.influencer_income += camp_inf.campaign_amt

        db.session.commit()
        return (
            jsonify({"message": "Ad request has been accepted successfully"}),
            200,
        )
    else:
        return jsonify({"error": "Request has not been received to accept"}), 404


@influencer.route("/rm-ad-req", methods=["DELETE"])
@role_required("influencer")
def rm_ad_req():
    data = request.get_json()
    inf_id = data.get("inf_id")
    camp_id = data.get("camp_id")

    campaign = Campaign.query.get(camp_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    influencer = Influencer.query.get(inf_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    camp_inf = CampaignInfluencer.query.filter_by(
        campaign_id=campaign.campaign_id, influencer_id=influencer.influencer_id
    ).first()

    if camp_inf:
        if camp_inf.status == "accepted":

            campaign.campaign_expenses -= camp_inf.campaign_amt
            influencer.influencer_income -= camp_inf.campaign_amt

        db.session.delete(camp_inf)
        db.session.commit()
        return (
            jsonify({"message": "Ad request has been removed successfully"}),
            200,
        )
    else:
        return jsonify({"error": "Request has not been received to remove"}), 404


@influencer.route("/get-graph-data")
@role_required("influencer")
def get_graph_data():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()

    campaigns_influencer = (
        db.session.query(Campaign.campaign_title, Campaign.campaign_expenses)
        .join(
            CampaignInfluencer,
            Campaign.campaign_id == CampaignInfluencer.campaign_id,
        )
        .filter(
            CampaignInfluencer.influencer_id == current_user.influencer_id,
            CampaignInfluencer.status == "accepted",
        )
        .all()
    )

    data = {
        campaign.campaign_title: campaign.campaign_expenses
        for campaign in campaigns_influencer
    }

    return jsonify(data)


@influencer.route("/get-pie-data")
@role_required("influencer")
def get_pie_data():
    user_email = get_jwt_identity()
    current_user = Influencer.query.filter_by(email=user_email).first()

    num_current_campaign = len(
        CampaignInfluencer.query.filter_by(
            influencer_id=current_user.influencer_id, status="accepted"
        ).all()
    )
    num_all_campaign = len(Campaign.query.all())
    num_not_current_campagin = int(num_all_campaign) - int(num_current_campaign)
    data = {
        "your_camp": num_current_campaign,
        "not_your_camp": num_not_current_campagin,
    }
    return jsonify(data)


@influencer.route("/delete-influencer", methods=["DELETE"])
@role_required("influencer")
def delete_influencer():
    influencer_id = request.json.get("influencer_id")
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    campaign_influencers = CampaignInfluencer.query.filter_by(
        influencer_id=influencer_id
    ).all()
    for ci in campaign_influencers:
        db.session.delete(ci)

    db.session.delete(influencer)
    del_inf_image(influencer.influencer_profile_image)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Influencer profile and related data have been removed successfully"
            }
        ),
        200,
    )


@influencer.route("/change-salary/<id>", methods=["PUT"])
@role_required("influencer")
def change_salary(id):
    camp_inf = CampaignInfluencer.query.get(id)
    if not camp_inf:
        return jsonify({"message": "Request not found", "status": "error"}), 404

    salary = request.json.get("salary")
    if salary and salary.strip():
        salary = int(salary.strip())
        if salary != camp_inf.campaign_amt:
            camp_inf.campaign_amt = salary
            db.session.commit()
            return (
                jsonify(
                    {"message": "Changed Salary Successfully", "status": "success"}
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {"message": "No change detected for Salary", "status": "error"}
                ),
                400,
            )
    else:
        return jsonify({"message": "Invalid salary input", "status": "error"}), 400
