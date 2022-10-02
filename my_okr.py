from config import Config
import datetime
import json
import requests
import urllib.request
from zoneinfo import ZoneInfo


class MyOkr():
    def __init__(self):
        self.config = Config()
        self.today = datetime.date.today()
        self.jst_today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

    """
    全員の OKR を取得する
    """
    def get_ours_okr(self, params):
        req = urllib.request.Request(
            f'{self.config.base_url}/api/okr/ours/get',
            json.dumps(params).encode(),
            self.config.headers
        )

        with urllib.request.urlopen(req) as res:
            body = json.load(res)

        return body

    """
    四半期情報を取得する
    """
    def get_quarter(self):
        req = urllib.request.Request(
            f'{self.config.base_url}/api/quarter/get',
            json.dumps({}).encode(),
            self.config.headers
        )

        with urllib.request.urlopen(req) as res:
            body = json.load(res)

        return body

    """
    Notion に貼り付けるとインラインデータベースになる Markdown テーブル書式のテキストを作成
    is_plaintext を True にすると、Slack 通知用の形式で取得できる
    """
    def get_str_okr_for_webhook(self, name, objective, is_more_detail=False, is_plaintext=False):
        if not objective:
            return None

        texts = {
            self.config.NOTION: self.init_text_for_webhook(name, is_plaintext, self.config.NOTION, is_more_detail),
        }

        for o in objective:
            texts = self.add_objective_to_text_for_webhook(o, texts, is_more_detail)

        return self.end_text_for_webhook(texts, is_plaintext)

    """
    Notion に貼り付けるとインラインデータベースになる Markdown テーブル書式のテキストを作成
    is_plaintext を True にすると、Slack 通知用の形式で取得できる
    """
    def get_str_okr_for_api(self, objectives, is_more_detail=False):
        texts = {
            self.config.NOTION: self.init_text_for_api(self.config.NOTION, is_more_detail),
        }

        for name, objective in objectives.items():
            if not objective:
                continue

            for o in objective:
                texts = self.add_objective_to_text_for_api(name, o, texts, is_more_detail)

        return texts

    """
    Slack API (Slack App) で該当する Slack チャンネルに Post する
    """
    def slack_post_via_api(self, text, bot_name, bot_emoji, channel_id, is_snipet=True):
        if self.config.is_debug:
            channel_id = self.config.channel_ids['default']

        if is_snipet:
            # content にスニペット内容を指定すればファイル生成しなくて済む
            requests.post('https://slack.com/api/files.upload', data={
                'token': self.config.slack_token,
                'channels': channel_id,
                'title': str(self.jst_today) + '-okr.md',
                'filename': str(self.jst_today) + "-okr.md",
                'filetype': "markdown",
                'content': text,
            })
        else:
            requests.post('https://slack.com/api/chat.postMessage', data={
                'token': self.config.slack_token,
                'channel': channel_id,
                'text': text,
                'filename': 'okr.md',
                'username': bot_name,
                'icon_emoji': bot_emoji,
                # ポストされるメンションの有効化
                'link_names': 1,
            })

    """
    Webhook で該当する Slack チャンネルに Post する
    specify_webhook_url で直接 webhook_url を指定することも可能
    """
    def slack_post_via_webhook(self, project_id, text, bot_name, bot_emoji, specify_webhook_url=None):
        webhook_url = None

        if specify_webhook_url is None:
            # project_id に紐づく webhook_url を検索
            for key, val in self.config.project_ids.items():
                if val == project_id:
                    webhook_url = self.config.webhook_urls[key]
                    break
        else:
            webhook_url = specify_webhook_url

        # 紐づく webhook_url がなかった場合、もしくはデバッグモード有効の場合はデフォルトチャンネルに通知する
        if (webhook_url is None) or (self.config.is_debug):
            webhook_url = self.config.webhook_urls['default']

        requests.post(webhook_url, json.dumps({
            'text': text,
            'username': bot_name,
            'icon_emoji': bot_emoji,
            # ポストされるメンションの有効化
            'link_names': 1,
        }))

    """
    メッセージ初期化 (Webhook)
    """
    def init_text_for_webhook(self, name, is_plaintext, target, is_more_detail):
        text = ''

        if is_plaintext:
            text += f'*{name}*\n'
            text += '```'

        if target == self.config.NOTION:
            if is_more_detail:
                text += '|Year|Quarter|Priority|Objective (Score)|Remarks|Impression|Key Result1 (Score)|Remarks1|Impression1|Key Result2 (Score)|Remarks2|Impression2|Key Result3 (Score)|Remarks3|Impression3|Comments|\n'
                text += '|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n'
            else:
                text += '|Year|Quarter|Priority|Objective (Score)|Key Result1 (Score)|Key Result2 (Score)|Key Result3 (Score)|Comments|\n'
                text += '|:-|:-|:-|:-|:-|:-|:-|:-|\n'

        return text

    """
    メッセージ初期化 (API)
    """
    def init_text_for_api(self, target, is_more_detail):
        text = ''

        if target == self.config.NOTION:
            if is_more_detail:
                text += '|Name|Year|Quarter|Priority|Objective (Score)|Remarks|Impression|Key Result1 (Score)|Remarks1|Impression1|Key Result2 (Score)|Remarks2|Impression2|Key Result3 (Score)|Remarks3|Impression3|Comments|\n'
                text += '|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n'
            else:
                text += '|Name|Year|Quarter|Priority|Objective (Score)|Key Result1 (Score)|Key Result2 (Score)|Key Result3 (Score)|Comments|\n'
                text += '|:-|:-|:-|:-|:-|:-|:-|:-|:-|\n'

        return text

    """
    Objective の情報をテキスト追加する
    """
    def add_objective_to_text_for_webhook(self, objective, texts, is_more_detail):
        okr = self.__get_okr_info(objective)
        str_quarter = self.__get_str_quarter(objective)

        if is_more_detail:
            texts[self.config.NOTION] += f"|{objective['year']}" + \
                f"|{str_quarter}" + \
                f"|{objective['priority']}" + \
                f"|{okr['objective_title']} ({objective['score']})" + \
                f"|{okr['str_objective_remarks']}" + \
                f"|{okr['str_objective_impression']}" + \
                f"|{okr['str_key_results'][0]}" + \
                f"|{okr['str_key_result_remarks'][0]}" + \
                f"|{okr['str_key_result_impressions'][0]}" + \
                f"|{okr['str_key_results'][1]}" + \
                f"|{okr['str_key_result_remarks'][1]}" + \
                f"|{okr['str_key_result_impressions'][1]}" + \
                f"|{okr['str_key_results'][2]}" + \
                f"|{okr['str_key_result_remarks'][2]}" + \
                f"|{okr['str_key_result_impressions'][2]}" + \
                f"|{okr['comment']}" + \
                '|\n'
        else:
            texts[self.config.NOTION] += f"|{objective['year']}" + \
                f"|{objective['quarter']}" + \
                f"|{objective['priority']}" + \
                f"|{okr['objective_title']} ({objective['score']})" + \
                f"|{okr['str_key_results'][0]}" + \
                f"|{okr['str_key_results'][1]}" + \
                f"|{okr['str_key_results'][2]}" + \
                f"|{okr['comment']}" + \
                '|\n'

        return texts

    """
    Objective の情報をテキスト追加する
    """
    def add_objective_to_text_for_api(self, name, objective, texts, is_more_detail):
        okr = self.__get_okr_info(objective)
        str_quarter = self.__get_str_quarter(objective)

        if is_more_detail:
            texts[self.config.NOTION] += f"|{name}" + \
                f"|{objective['year']}" + \
                f"|{str_quarter}" + \
                f"|{objective['priority']}" + \
                f"|{okr['objective_title']} ({objective['score']})" + \
                f"|{okr['str_objective_remarks']}" + \
                f"|{okr['str_objective_impression']}" + \
                f"|{okr['str_key_results'][0]}" + \
                f"|{okr['str_key_result_remarks'][0]}" + \
                f"|{okr['str_key_result_impressions'][0]}" + \
                f"|{okr['str_key_results'][1]}" + \
                f"|{okr['str_key_result_remarks'][1]}" + \
                f"|{okr['str_key_result_impressions'][1]}" + \
                f"|{okr['str_key_results'][2]}" + \
                f"|{okr['str_key_result_remarks'][2]}" + \
                f"|{okr['str_key_result_impressions'][2]}" + \
                f"|{okr['comment']}" + \
                '|\n'
        else:
            texts[self.config.NOTION] += f"|{name}" + \
                f"|{objective['year']}" + \
                f"|{objective['quarter']}" + \
                f"|{objective['priority']}" + \
                f"|{okr['objective_title']} ({objective['score']})" + \
                f"|{okr['str_key_results'][0]}" + \
                f"|{okr['str_key_results'][1]}" + \
                f"|{okr['str_key_results'][2]}" + \
                f"|{okr['comment']}" + \
                '|\n'

        return texts

    """
    メッセージ終了部分の処理
    """
    def end_text_for_webhook(self, texts, is_plaintext):
        for id, text in texts.items():
            if is_plaintext:
                text += '```'
                texts[id] = text

        return texts

    def __get_okr_info(self, objective):
        objective_title = ''.join(objective['objective'].splitlines())
        objective_title = f"[{objective_title}]({self.config.base_url}/key_result?objective_id={objective['id']})"
        str_objective_remarks = '' if objective['remarks'] is None else ''.join(objective['remarks'].splitlines())
        str_objective_impression = '' if objective['impression'] is None else ''.join(objective['impression'].splitlines())
        str_key_results = ['', '', '']
        str_key_result_remarks = ['', '', '']
        str_key_result_impressions = ['', '', '']
        for index, key_result in enumerate(objective['key_results']):
            k = key_result['key_result']
            s = key_result['score']
            r = key_result['remarks']
            i = key_result['impression']

            if (k is None) and (s == 0):
                continue

            k = '' if k is None else ''.join(k.splitlines())
            r = '' if r is None else ''.join(r.splitlines())
            i = '' if i is None else ''.join(i.splitlines())

            str_key_results[index] = f"{k} ({key_result['score']})"
            str_key_result_remarks[index] = f"{r}"
            str_key_result_impressions[index] = f"{i}"

        comment = ''
        count = 1
        for c in objective['comments']:
            # 表示するコメントは 3 件までとする
            if count <= 3:
                comment += f'【コメント{count}】'
                comment += ''.join(c['comment'].splitlines())
            count += 1

        return {
            'objective_title': objective_title,
            'str_objective_remarks': str_objective_remarks,
            'str_objective_impression': str_objective_impression,
            'str_key_results': str_key_results,
            'str_key_result_remarks': str_key_result_remarks,
            'str_key_result_impressions': str_key_result_impressions,
            'comment': comment,
        }

    def __get_str_quarter(self, objective):
        str_quarter = ""

        if objective['quarter'] == 0:
            str_quarter = '通年'
        else:
            str_quarter = f"{objective['quarter']}Q"

        return str_quarter
