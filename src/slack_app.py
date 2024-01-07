import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# 環境変数の読み込み
load_dotenv()

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# スケジューリングされたジョブの関数定義
def send_message():
    """Slackチャンネルに定期的なメッセージを送信する。"""
    channel_id = os.environ["SLACK_CHANNEL_ID"]  # メッセージを送信するチャンネルID
    app.client.chat_postMessage(channel=channel_id, text="Hello Slack!")

# アプリに対するメンションに応答する関数定義
@app.event("app_mention")
def handle_mention(event, say):
    """アプリに対するメンションに応答する。"""
    # メンションされたメッセージのテキストを取得
    text = event['text']
    # メンションを除去する（例：<@U123ABCD>）
    cleaned_text = re.sub(r"<@[\w]+>", "", text).strip()
    # メンションを除いたテキストを返信
    say(cleaned_text)

# APSchedulerの設定とスケジューラーの開始
scheduler = BackgroundScheduler()
scheduler.add_job(send_message, 'cron', hour=14, minute=55)
scheduler.start()

# アプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
