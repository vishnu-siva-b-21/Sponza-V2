from flask import (
    Blueprint,
    request,
    jsonify,
)
from flask_jwt_extended import get_jwt_identity
from sponza_app.models import (
    Sponsor,
    Campaign,
    Influencer,
    CampaignInfluencer,
    role_required,
)
from sponza_app import db, bcrypt
from sponza_app.modules.sponsor.utils import (
    del_save_image,
    return_sponsor_profile_image,
    return_inf_profile_image,
    return_campaign_image,
    save_camp_image,
    del_save_camp_image,
    del_spon_image,
    del_camp_image,
)
from datetime import datetime, date


sponsor = Blueprint("sponsor", __name__)


@sponsor.route("/base")
@role_required("sponsor")
def sponsor_base():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    image = "http://127.0.0.1:5000/" + return_sponsor_profile_image(
        current_user.sponsor_profile_image
    )

    return jsonify(
        {
            "sponsor": {
                "name": current_user.sponsor_company_name,
                "image": image,
            }
        }
    )


@sponsor.route("/get-graph-data")
@role_required("sponsor")
def get_graph_data():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.sponsor_id).all()
    data = {camp.campaign_title: camp.campaign_expenses for camp in campaigns}
    return jsonify(data)


@sponsor.route("/get-pie-data")
@role_required("sponsor")
def get_pie_data():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    num_current_campaign = len(
        Campaign.query.filter_by(sponsor_id=current_user.sponsor_id).all()
    )
    num_all_campaign = len(Campaign.query.all())
    num_not_current_campagin = int(num_all_campaign) - int(num_current_campaign)
    data = {
        "your_camp": num_current_campaign,
        "not_your_camp": num_not_current_campagin,
    }
    return jsonify(data)


@sponsor.route("/api/dashboard")
@role_required("sponsor")
def sponsor_api_dashboard():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    if not current_user:
        return jsonify({"error": "Sponsor not found"}), 404

    image = return_sponsor_profile_image(current_user.sponsor_profile_image)

    sponsor_campaigns = current_user.campaigns

    # Retrieve all CampaignInfluencer records with status "inf_sent_pending"
    pending_requests = []
    for camp in sponsor_campaigns:
        pending_influencers = CampaignInfluencer.query.filter_by(
            campaign_id=camp.campaign_id, status="inf_sent_pending"
        ).all()
        pending_requests.extend(pending_influencers)

    # Prepare serialized data
    campaigns_data = []
    for camp in sponsor_campaigns:
        total_camp_days = (camp.campaign_end_date - camp.campaign_start_date).days
        completed_camp_days = (date.today() - camp.campaign_start_date).days
        progress = (
            int((completed_camp_days / total_camp_days) * 100)
            if total_camp_days > 0
            else 0
        )

        campaigns_data.append(
            {
                "id": camp.campaign_id,
                "title": camp.campaign_title,
                "image": "http://127.0.0.1:5000/"
                + return_campaign_image(camp.campaign_profile_image),
                "progress": progress,
                "flag": camp.admin_flag,
                "start_date": str(camp.campaign_start_date),
                "end_date": str(camp.campaign_end_date),
                "expenses": camp.campaign_expenses,
            }
        )

    total_expenses = sum(camp["expenses"] for camp in campaigns_data)

    response_data = {
        "sponsor_name": current_user.sponsor_company_name,
        "image": image,
        "user_num_camp": len(sponsor_campaigns),
        "num_camp": Campaign.query.count(),
        "total_expenses": total_expenses,
        "num_pending_requests": len(pending_requests),
        "campaigns": campaigns_data,
    }

    return jsonify(response_data)


@sponsor.route("/campaigns")
@role_required("sponsor")
def sponsor_campaigns():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    sponsor_campaigns = Campaign.query.filter_by(
        sponsor_id=current_user.sponsor_id
    ).all()
    campaigns_data = []

    for camp in sponsor_campaigns:
        campaigns_data.append(
            {
                "id": camp.campaign_id,
                "title": camp.campaign_title,
                "image": "http://127.0.0.1:5000/"
                + return_campaign_image(camp.campaign_profile_image),
                "desc": camp.campaign_desc,
                "start_date": str(camp.campaign_start_date),
                "end_date": str(camp.campaign_end_date),
            }
        )

    return jsonify(
        sponsor_name=current_user.sponsor_company_name,
        campaigns=campaigns_data,
    )


@sponsor.route("/add-campaign", methods=["POST"])
@role_required("sponsor")
def add_campaign():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()

    file_name = "campaign.png"
    if "profile_pic" in request.files:
        profile_pic = request.files["profile_pic"]
        file_name = save_camp_image(profile_pic)

    campaign = Campaign(
        campaign_title=request.form.get("title").strip(),
        campaign_desc=request.form.get("desc"),
        campaign_end_date=datetime.strptime(
            request.form.get("end_date"), "%Y-%m-%d"
        ).date(),
        campaign_visibility=request.form.get("campaign_visibility") or "public",
        campaign_goals=request.form.get("campaign_goals"),
        campaign_profile_image=file_name,
        sponsor_id=current_user.sponsor_id,
    )
    db.session.add(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign Added Successfully", "status": "success"})


@sponsor.route("/profile")
@role_required("sponsor")
def sponsor_profile():
    user_email = get_jwt_identity()
    current_user = Sponsor.query.filter_by(email=user_email).first()
    sponsor_details = {}
    sponsor_details["sponsor_id"] = current_user.sponsor_id
    sponsor_details["sponsor_name"] = current_user.sponsor_company_name
    sponsor_details["email"] = current_user.email
    sponsor_details["industry"] = current_user.industry
    sponsor_details["image"] = "http://127.0.0.1:5000/" + return_sponsor_profile_image(
        current_user.sponsor_profile_image
    )
    return jsonify(sponsor_details)


@sponsor.route("/update-profile", methods=["PUT"])
@role_required("sponsor")
def update_profile():
    try:
        user_email = get_jwt_identity()
        current_user = Sponsor.query.filter_by(email=user_email).first()

        if not current_user:
            return jsonify({"success": False, "message": "User not found"}), 404

        file_name = None
        if "profile_pic" in request.files:
            profile_pic = request.files["profile_pic"]
            file_name = del_save_image(profile_pic, current_user.sponsor_profile_image)

        Sponsor.query.filter_by(email=current_user.email).update(
            {
                "sponsor_company_name": request.form.get("company_name").strip(),
                "email": request.form.get("email").strip(),
                "industry": request.form.get("industry").strip(),
                "sponsor_profile_image": file_name
                or current_user.sponsor_profile_image,
            }
        )
        db.session.commit()
        return jsonify({"success": True, "message": "Profile updated successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": "Internal Server Error"}), 500


@sponsor.route("/update-camp-image/<id>", methods=["PUT"])
@role_required("sponsor")
def update_camp_image(id):
    if "camp_image" not in request.files:
        return jsonify({"message": "No file part", "status": "error"}), 400

    file = request.files["camp_image"]
    old_file = request.form.get("file")  # Get old file path from the form

    file_name = del_save_camp_image(file, old_file) if file else old_file

    campaign = Campaign.query.get(id)
    if campaign:
        campaign.campaign_profile_image = file_name
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Campaign Image updated successfully",
                    "status": "success",
                    "image_path": file_name,
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "Campaign not found", "status": "error"}), 404


@sponsor.route("/details/<id>")
@role_required("sponsor")
def sponsor_details(id):
    campaign = Campaign.query.get(id)
    campaign_dict = {}
    if campaign:
        campaign_dict["campaign_id"] = campaign.campaign_id
        campaign_dict["campaign_title"] = campaign.campaign_title
        campaign_dict["campaign_desc"] = campaign.campaign_desc
        campaign_dict["campaign_start_date"] = campaign.campaign_start_date
        campaign_dict["campaign_end_date"] = campaign.campaign_end_date
        campaign_dict["campaign_expenses"] = campaign.campaign_expenses
        campaign_dict["campaign_visibility"] = (
            True if campaign.campaign_visibility == "private" else False
        )
        campaign_dict["campaign_goals"] = campaign.campaign_goals
        campaign_dict["admin_flag"] = campaign.admin_flag
        campaign_dict["admin_flag_time"] = campaign.admin_flag_time
        campaign_dict["campaign_profile_image"] = (
            "http://127.0.0.1:5000/"
            + return_campaign_image(campaign.campaign_profile_image)
        )
        camp_sent_pending = []
        inf_sent_pending = []
        accpted_inf = []

        for inf in CampaignInfluencer.query.filter_by(
            campaign_id=id, status="camp_sent_pending"
        ).all():
            inf_data = {
                "main_id": inf.ci_id,
                "influencer_id": inf.influencer.influencer_id,
                "email": inf.influencer.email,
                "influencer_user_name": inf.influencer.influencer_user_name,
                "influencer_profile_image": "http://127.0.0.1:5000/"
                + return_inf_profile_image(inf.influencer.influencer_profile_image),
                "camp_pay": inf.campaign_amt,
            }
            camp_sent_pending.append(inf_data)

        for inf in CampaignInfluencer.query.filter_by(
            campaign_id=id, status="inf_sent_pending"
        ).all():
            inf_data = {
                "main_id": inf.ci_id,
                "influencer_id": inf.influencer.influencer_id,
                "email": inf.influencer.email,
                "influencer_niche": inf.influencer.influencer_niche,
                "influencer_social_media_platform": inf.influencer.influencer_social_media_platform,
                "influencer_social_media_link": inf.influencer.influencer_social_media_link,
                "influencer_user_name": inf.influencer.influencer_user_name,
                "influencer_profile_image": "http://127.0.0.1:5000/"
                + return_inf_profile_image(inf.influencer.influencer_profile_image),
                "amt": inf.campaign_amt,
            }
            inf_sent_pending.append(inf_data)

        for inf in CampaignInfluencer.query.filter_by(
            campaign_id=id, status="accepted"
        ).all():
            inf_data = {
                "main_id": inf.ci_id,
                "influencer_id": inf.influencer.influencer_id,
                "influencer_user_name": inf.influencer.influencer_user_name,
                "email": inf.influencer.email,
                "influencer_niche": inf.influencer.influencer_niche,
                "influencer_social_media_link": inf.influencer.influencer_social_media_link,
                "influencer_social_media_platform": inf.influencer.influencer_social_media_platform,
                "influencer_profile_image": "http://127.0.0.1:5000/"
                + return_inf_profile_image(inf.influencer.influencer_profile_image),
                "amt": inf.campaign_amt,
            }
            accpted_inf.append(inf_data)
        return jsonify(
            camp=campaign_dict,
            camp_sent_pending=camp_sent_pending,
            inf_sent_pending=inf_sent_pending,
            accpted_inf=accpted_inf,
        )


@sponsor.route("/change-details/<id>", methods=["PUT"])
def sponsor_change_details(id):
    campaign = Campaign.query.get_or_404(id)
    data = request.json
    updated = False

    if "campaign_title" in data:
        campaign_title = data["campaign_title"].strip()
        if campaign_title and campaign_title != campaign.campaign_title:
            campaign.campaign_title = campaign_title
            updated = True

    if "campaign_desc" in data:
        campaign_desc = data["campaign_desc"].strip()
        if campaign_desc and campaign_desc != campaign.campaign_desc:
            campaign.campaign_desc = campaign_desc
            updated = True

    if "campaign_goals" in data:
        campaign_goals = data["campaign_goals"].strip()
        if campaign_goals and campaign_goals != campaign.campaign_goals:
            campaign.campaign_goals = campaign_goals
            updated = True

    if "campaign_end_date" in data:
        try:
            campaign_end_date = data["campaign_end_date"]
            if campaign_end_date and campaign_end_date != str(
                campaign.campaign_end_date
            ):
                campaign.campaign_end_date = datetime.strptime(
                    campaign_end_date, "%Y-%m-%d"
                ).date()
                updated = True
        except ValueError:
            return jsonify({"message": "Invalid date format", "status": "error"}), 400

    if "campaign_visibility" in data:
        campaign_visibility = "private" if data["campaign_visibility"] else "public"
        if campaign_visibility and campaign_visibility != campaign.campaign_visibility:
            campaign.campaign_visibility = campaign_visibility
            updated = True

    if updated:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Campaign details updated successfully",
                    "status": "success",
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {"message": "No changes detected or invalid input", "status": "error"}
            ),
            400,
        )


@sponsor.route("/search-inf", methods=["POST"])
@role_required("sponsor")
def search_inf():
    data = request.get_json()
    query = data.get("query", "").lower()

    influencers = Influencer.query.filter(
        (Influencer.influencer_user_name.contains(query))
        | (Influencer.email.contains(query))
        | (Influencer.influencer_niche.contains(query))
        | (Influencer.influencer_social_media_platform.contains(query))
    ).all()

    user_list = [
        {
            "id": influencer.influencer_id,
            "email": influencer.email,
            "username": influencer.influencer_user_name,
            "image": "http://127.0.0.1:5000/"
            + return_inf_profile_image(influencer.influencer_profile_image),
        }
        for influencer in influencers
    ]

    return jsonify({"users": user_list})


@sponsor.route("/send-ad-request/<camp_id>", methods=["POST"])
@role_required("sponsor")
def send_ad_request(camp_id):
    ad_data = request.json
    inf_id = ad_data["adInfluencerid"]
    camp_pay = ad_data["adPayment"]

    campaign = Campaign.query.get(camp_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    if campaign.admin_flag == "True":
        return (
            jsonify(
                {
                    "error": "This Campaign is Flagged by admin, Please check your email for more details."
                }
            ),
            405,
        )
    influencer = Influencer.query.get(inf_id)
    if not influencer:
        return jsonify({"error": "Influencer not found"}), 404

    camp_inf = CampaignInfluencer.query.filter_by(
        campaign_id=campaign.campaign_id, influencer_id=influencer.influencer_id
    ).first()
    if camp_inf:
        if camp_inf.status == "camp_sent_pending":
            return jsonify({"error": "Ad request already sent"}), 409
        elif camp_inf.status == "inf_sent_pending":
            return jsonify({"error": "Ad request already recieved"}), 409
        elif camp_inf.status == "accepted":
            return jsonify({"error": "Ad request already accepted"}), 409
        else:
            return jsonify({"error": "Error"}), 404

    campaign_influencer = CampaignInfluencer(
        campaign_id=campaign.campaign_id,
        influencer_id=influencer.influencer_id,
        campaign_amt=camp_pay,
        status="camp_sent_pending",
    )

    db.session.add(campaign_influencer)
    db.session.commit()

    return jsonify({"message": "Ad request sent successfully"}), 200


@sponsor.route("/accept-ad-req", methods=["PUT"])
@role_required("sponsor")
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


@sponsor.route("/rm-ad-req", methods=["DELETE"])
@role_required("sponsor")
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


@sponsor.route("/delete-camp/<id>", methods=["DELETE"])
@role_required("sponsor")
def delete_camp(id):
    try:
        campaign = Campaign.query.get(id)
        if not campaign:
            return jsonify(message=f"Campaign Not Found", status="error")
        for ci in campaign.campaign_influencers:
            influencer = Influencer.query.get(ci.influencer_id)
            if influencer:
                influencer.influencer_income -= ci.campaign_amt
                db.session.add(influencer)
            db.session.delete(ci)

        db.session.delete(campaign)
        del_camp_image(campaign.campaign_profile_image)
        db.session.commit()
        return jsonify(message="Campaign deleted successfully", status="success")
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"{str(e)}", status="error")


@sponsor.route("/delete-sponsor", methods=["DELETE"])
@role_required("sponsor")
def delete_sponsor():
    sponsor_id = request.json.get("sponsor_id")
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        return jsonify({"error": "Sponsor not found"}), 404
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    for campaign in campaigns:
        CampaignInfluencer.query.filter_by(campaign_id=campaign.campaign_id).delete()
        db.session.delete(campaign)
    db.session.delete(sponsor)
    del_spon_image(sponsor.sponsor_profile_image)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Sponsor profile and related data have been removed successfully"
            }
        ),
        200,
    )


@sponsor.route("/change-salary/<id>", methods=["PUT"])
@role_required("sponsor")
def change_salary(id):
    camp_inf = CampaignInfluencer.query.get(id)
    if not camp_inf:
        return jsonify(message="Request not found", status="error")
    salary = request.json.get("salary")
    updated = False
    if salary:
        salary = salary.strip()
        if salary and int(salary) != camp_inf.campaign_amt:
            camp_inf.campaign_amt = int(salary)
            updated = True
            return jsonify(message="Changed Salary Successfully", status="success")
        else:
            return jsonify(message="No change detected for Salary", status="error")

    if updated:
        db.session.commit()
    else:
        return jsonify(message="Invalid or No changes detected!", status="error")


@sponsor.route("/monthly-report-data/<id>/<month>/<year>")
def monthly_report_data(id, month, year):
    if month == "1":
        month = "12"
        year = str(int(year) - 1)
    else:
        month = str(int(month) - 1)
    sponsor_campaigns = (
        Campaign.query.filter_by(sponsor_id=id)
        .filter(
            db.extract("month", Campaign.campaign_start_date) == month,
            db.extract("year", Campaign.campaign_start_date) == year,
        )
        .all()
    )

    campaigns_data = []

    for camp in sponsor_campaigns:
        campaigns_data.append(
            {
                "id": camp.campaign_id,
                "title": camp.campaign_title,
                "image": "http://127.0.0.1:5000/"
                + return_campaign_image(camp.campaign_profile_image),
                "desc": camp.campaign_desc,
                "start_date": str(camp.campaign_start_date),
                "end_date": str(camp.campaign_end_date),
                "visiblity": str(camp.campaign_visibility),
                "goals": str(camp.campaign_goals),
                "budget": str(camp.campaign_expenses),
            }
        )

    return jsonify(
        campaigns=campaigns_data,
    )


@sponsor.route("/get-monthly-report-graph-data/<id>/<month>/<year>")
def get_monthly_report_graph_data(id, month, year):
    if month == "1":
        month = "12"
        year = str(int(year) - 1)
    else:
        month = str(int(month) - 1)
    sponsor_campaigns = (
        Campaign.query.filter_by(sponsor_id=id)
        .filter(
            db.extract("month", Campaign.campaign_start_date) == month,
            db.extract("year", Campaign.campaign_start_date) == year,
        )
        .all()
    )
    data = {camp.campaign_title: camp.campaign_expenses for camp in sponsor_campaigns}
    return jsonify(data)
