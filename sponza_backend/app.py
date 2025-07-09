from datetime import datetime
from sponza_app import create_app
from sponza_app.tasks import (
    daily_remainder_influencer,
    delete_ended_campaigns,
    delete_flagged_campaigns,
    delete_flagged_users,
    monthly_report_sponsor,
)
from celery.schedules import crontab


app = create_app()
celery_app = app.extensions["celery"]


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        30.0, delete_ended_campaigns.s(), name="Delete Ended Campaigns"
    )
    sender.add_periodic_task(
        30.0, delete_flagged_campaigns.s(), name="Delete Flagged Campaigns"
    )
    sender.add_periodic_task(
        30.0, delete_flagged_users.s(), name="Delete Flagged Users"
    )
    # Task to run every day at 12:00 PM
    sender.add_periodic_task(
        crontab(hour=12, minute=0),
        daily_remainder_influencer.s(),
        name="Daily remainder for influencer",
    )

    # Task to run on the 1st of every month at 3:00 PM
    sender.add_periodic_task(
        crontab(hour=15, minute=00, day_of_month=1),
        monthly_report_sponsor.s(datetime.today().date()),
        name="Monthly Report for Sponsor",
    )


if __name__ == "__main__":
    app.run(debug=1)
