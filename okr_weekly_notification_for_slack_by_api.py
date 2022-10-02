from my_okr import MyOkr
import sys


class OkrWeeklyNotificationForSlackByApi():
    def __init__(self, year, quarter_id, is_more_detail, is_include_full_year):
        self.year = year
        self.quarter_id = quarter_id
        self.is_more_detail = is_more_detail
        self.is_include_full_year = is_include_full_year

    def run(self):
        okr = MyOkr()

        result = okr.get_ours_okr({
            'year': self.year,
            'quarter_id': self.quarter_id,
            'user_id': None,
            'is_archived': '0',
            'is_include_full_year': self.is_include_full_year
        })

        texts = okr.get_str_okr_for_api(result['objectives'], self.is_more_detail)

        if texts is not None:
            okr.slack_post_via_api(texts[okr.config.NOTION], 'Weekly OKR', ':bar_chart:', okr.config.channel_ids['okr_weekly_notification_for_notion'], True)

        print('Slack Post About Weekly OKR Done!')


input = {
    'year': None,
    'quarter_id': None,
    'is_more_detail': False,
    'is_include_full_year': False,
}

for index, arg in enumerate(sys.argv):
    if index == 1:
        input['year'] = arg

    if index == 2:
        input['quarter_id'] = arg

    if index == 3:
        input['is_more_detail'] = bool(arg)

    if index == 4:
        input['is_include_full_year'] = bool(arg)

okr_weekly_notification_for_slack_by_api = OkrWeeklyNotificationForSlackByApi(input['year'], input['quarter_id'], input['is_more_detail'], input['is_include_full_year'])
okr_weekly_notification_for_slack_by_api.run()
