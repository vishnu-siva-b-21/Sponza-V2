from sponza_app import db
from sponza_app.models import CampaignInfluencer, Influencer
from celery import shared_task
from sponza_app.modules.influencer.utils import remainder_influencer_request_nos
from collections import Counter
from datetime import datetime, timedelta, date
from sponza_app.models import Influencer, Campaign, Sponsor, CampaignInfluencer
from sponza_app.modules.sponsor.utils import (
    del_camp_image,
    del_spon_image,
    send_monthly_report_mail,
)
from sponza_app.modules.influencer.utils import del_inf_image


@shared_task()
def daily_remainder_influencer():
    reqs = []
    for req in CampaignInfluencer.query.all():
        if req.status == "camp_sent_pending":
            influencer = Influencer.query.get(req.influencer_id)
            reqs.append(influencer)
    counts = Counter(reqs)
    for inf in counts:
        remainder_influencer_request_nos(inf, counts[inf])
    return counts


@shared_task()
def monthly_report_sponsor(report_date):
    list = []
    year = report_date.year
    month = report_date.month
    for spn in Sponsor.query.all():
        list.append(spn.email)
        send_monthly_report_mail(spn, month, year)
    if len(list) != 0:
        return f"Mail Sent users - {list}"
    else:
        return "Mail not sent "


@shared_task()
def delete_ended_campaigns():
    ended_campaigns = Campaign.query.filter(
        date.today() >= Campaign.campaign_end_date
    ).all()
    list = []
    if ended_campaigns:
        for campaign in ended_campaigns:
            list.append(
                f"{campaign.campaign_title}: {date.today() >= campaign.campaign_end_date}"
            )
            for ci in campaign.campaign_influencers:
                influencer = Influencer.query.get(ci.influencer_id)
                if influencer:
                    influencer.influencer_income -= ci.campaign_amt
                    db.session.add(influencer)
                db.session.delete(ci)
            db.session.delete(campaign)
            del_camp_image(campaign.campaign_profile_image)
        db.session.commit()
        return f"{list} Ended Campaigns - Deleted"
    else:
        return "No Ended Campaigns"


@shared_task()
def delete_flagged_campaigns():
    time_now = datetime.now()
    expired_time_threshold = time_now - timedelta(hours=24)
    expired_campaigns = Campaign.query.filter(
        Campaign.admin_flag == "True",
        Campaign.admin_flag_time <= expired_time_threshold,
    ).all()
    list = []
    if expired_campaigns:
        for campaign in expired_campaigns:
            list.append(
                f"{campaign.campaign_title}: {time_now >= campaign.admin_flag_time + timedelta(hours=24)}"
            )
            for ci in campaign.campaign_influencers:
                influencer = Influencer.query.get(ci.influencer_id)
                if influencer:
                    influencer.influencer_income -= ci.campaign_amt
                    db.session.add(influencer)
                db.session.delete(ci)
            db.session.delete(campaign)
            del_camp_image(campaign.campaign_profile_image)
        db.session.commit()
        return f"{list} Expired Campaigns - Deleted"
    else:
        return "No Expired Campaigns"


@shared_task()
def delete_flagged_users():
    time_now = datetime.now()
    expired_time_threshold = time_now - timedelta(hours=240)

    list = []
    expired_influencers = Influencer.query.filter(
        Influencer.admin_flag == "True",
        Influencer.admin_flag_time <= expired_time_threshold,
    ).all()
    for influencer in expired_influencers:
        CampaignInfluencer.query.filter_by(
            influencer_id=influencer.influencer_id
        ).delete()
        del_inf_image(influencer.influencer_profile_image)
        list.append(
            f"{influencer.influencer_user_name}: {time_now >= influencer.admin_flag_time + timedelta(hours=240)}"
        )
        db.session.delete(influencer)

    expired_sponsors = Sponsor.query.filter(
        Sponsor.admin_flag == "True",
        Sponsor.admin_flag_time <= expired_time_threshold,
    ).all()
    for sponsor in expired_sponsors:
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
        for campaign in campaigns:
            CampaignInfluencer.query.filter_by(
                campaign_id=campaign.campaign_id
            ).delete()
            db.session.delete(campaign)
        del_spon_image(sponsor.sponsor_profile_image)
        list.append(
            f"{sponsor.sponsor_company_name}: {time_now >= sponsor.admin_flag_time + timedelta(hours=240)}"
        )
        db.session.delete(sponsor)
    db.session.commit()
    if len(list) != 0:
        return f"{list} Expired users - Deleted"
    else:
        return "No Expired users"
