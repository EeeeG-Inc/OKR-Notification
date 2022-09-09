from dotenv import load_dotenv
import os

load_dotenv()


class Config():
    NOTION = 1

    def __init__(self):
        is_debug = os.getenv('IS_DEBUG')

        if is_debug is None:
            self.is_debug = False
        else:
            self.is_debug = bool(int(is_debug))

        self.base_url = os.getenv('BASE_URL')
        api_token = os.getenv('API_TOKEN')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_token}',
        }

        self.webhook_urls = {
            'default': os.getenv('WEBHOOK_URL_DEFAULT'),
            'notion': os.getenv('WEBHOOK_URL_FOR_NOTION'),
        }

        self.channel_ids = {
            'default': os.getenv('CHANNEL_ID_DEFAULT'),
            'okr_weekly_notification_for_notion': os.getenv('CHANNEL_ID_OKR_WEEKLY_NOTIFICATION_FOR_NOTION'),
        }

        self.slack_token = os.getenv('SLACK_TOKEN')
