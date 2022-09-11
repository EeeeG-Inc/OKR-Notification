from my_okr import MyOkr
import sys


class OkrWeeklyNotificationForSlackByWebhook():
    def __init__(self, year, quarter_id, is_more_detail, user_id):
        self.year = year
        self.quarter_id = quarter_id
        self.is_more_detail = is_more_detail
        self.user_id = user_id

    def run(self):
        okr = MyOkr()

        result = okr.get_ours_okr({
            'year': self.year,
            'quarter_id': self.quarter_id,
            'user_id': self.user_id,
            'is_archived': '0',
        })

        for name, objective in result['objectives'].items():
            texts = okr.get_str_okr_for_webhook(name, objective, self.is_more_detail, True)

            if texts is not None:
                okr.slack_post_via_webhook(None, texts[okr.config.NOTION], 'Weekly OKR', ':bar_chart:', okr.config.webhook_urls['notion'])

        print('Slack Post About Weekly OKR Done!')


input = {
    'year': None,
    'quarter_id': None,
    'is_more_detail': False,
    'user_id': None,
}

for index, arg in enumerate(sys.argv):
    if index == 1:
        input['year'] = arg

    if index == 2:
        input['quarter_id'] = arg

    if index == 3:
        input['is_more_detail'] = bool(arg)

    if index == 4:
        input['user_id'] = arg


okr_weekly_notification_for_slack_by_webhook = OkrWeeklyNotificationForSlackByWebhook(input['year'], input['quarter_id'], input['is_more_detail'], input['user_id'])
okr_weekly_notification_for_slack_by_webhook.run()
