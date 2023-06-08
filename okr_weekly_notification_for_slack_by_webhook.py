from my_okr import MyOkr
import sys


class OkrWeeklyNotificationForSlackByWebhook():
    def __init__(self, year, quarter_id, is_more_detail, user_id, is_include_full_year):
        self.year = year
        self.quarter_id = quarter_id
        self.is_more_detail = is_more_detail
        self.user_id = user_id
        self.is_include_full_year = is_include_full_year

    def run(self):
        okr = MyOkr()

        result = okr.get_ours_okr({
            'year': self.year,
            'quarter_id': self.quarter_id,
            'user_id': self.user_id,
            'is_archived': '0',
            'is_include_full_year': self.is_include_full_year
        })

        for name, objective in result['objectives'].items():
            texts = okr.get_str_okr_for_webhook(name, objective, self.is_more_detail, True)

            if texts is not None:
                okr.slack_post_via_webhook(None, texts[okr.config.NOTION], 'Weekly OKR', ':bar_chart:', okr.config.webhook_urls['notion'])
            else:
                print('このユーザは OKR を設定していません' )

        print('Slack Post About Weekly OKR Done!')


input = {
    'year': None,
    'quarter_id': None,
    'is_more_detail': False,
    'user_id': None,
    'is_include_full_year': False,
}

for index, arg in enumerate(sys.argv):
    if index == 1:
        input['year'] = None if arg == 'this_year_at_today' else arg

    if index == 2:
        input['quarter_id'] = None if arg == 'this_quarter_at_today' else arg

    if index == 3:
        input['is_more_detail'] = bool(arg)

    if index == 4:
        input['user_id'] = arg

    if index == 5:
        input['is_include_full_year'] = bool(arg)

okr_weekly_notification_for_slack_by_webhook = OkrWeeklyNotificationForSlackByWebhook(input['year'], input['quarter_id'], input['is_more_detail'], input['user_id'], input['is_include_full_year'])
okr_weekly_notification_for_slack_by_webhook.run()
