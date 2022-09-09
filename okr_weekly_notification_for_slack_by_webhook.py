from my_okr import MyOkr
import sys


class OkrWeeklyNotificationForSlackByWebhook():
    def __init__(self, year, quarter_id):
        self.year = year
        self.quarter_id = quarter_id

    def run(self):
        okr = MyOkr()

        result = okr.get_ours_okr({
            'year': year,
            'quarter_id': quarter_id,
            'is_archived': '0',
        })

        for name, objective in result['objectives'].items():
            texts = okr.get_str_okr_for_webhook(name, objective, True)

            if texts is not None:
                okr.slack_post_via_webhook(None, texts[okr.config.NOTION], 'Weekly OKR', ':bar_chart:', okr.config.webhook_urls['notion'])

        print('Slack Post About Weekly OKR Done!')


args = sys.argv
year = args[1]
quarter_id = args[2]

okr_weekly_notification_for_slack_by_webhook = OkrWeeklyNotificationForSlackByWebhook(year, quarter_id)
okr_weekly_notification_for_slack_by_webhook.run()
