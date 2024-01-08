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
    user_id = os.environ["MENTION_USER_ID"]  # メンションするユーザーID
    # メンションを含むメッセージを作成
    message_text = f"<@{user_id}> おはようございます！"
    app.client.chat_postMessage(channel=channel_id, text=message_text)

# アプリに対するメンションに応答する関数定義
@app.event("app_mention")
def handle_mention(event, say):
    """アプリに対するメンションに応答する。"""
    # メンションされたメッセージのテキストを取得
    text = event['text']
    # メンションを除去する
    cleaned_text = re.sub(r"<@[\w]+>", "", text).strip()

    # テキストが4桁の数字であるかチェック
    if re.match(r"^\d{4}$", cleaned_text):
        # 4桁の数字ならそのまま返信
        # 上2桁と下2桁に分割
        upper_two_digits = int(cleaned_text[:2])
        lower_two_digits = int(cleaned_text[2:])

        # 上2桁が0～23、下2桁が0～59の範囲内かチェック
        if 0 <= upper_two_digits <= 23 and 0 <= lower_two_digits <= 59:

            # 既存のジョブを削除
            if scheduler.get_job(job_name):
                scheduler.remove_job(job_name)

            # 新しい時間でジョブを追加
            scheduler.add_job(send_message, 'cron', hour=upper_two_digits, minute=lower_two_digits, id=job_name)

            # 条件を満たしている場合のメッセージ
            say(f"設定された時間: {upper_two_digits}時{lower_two_digits}分")
        else:
            # 条件を満たさない場合のメッセージ
            say("時間は上2桁が0～23、下2桁が0～59の範囲で指定してください。")
    else:
        # 4桁の数字でなければ、4桁の数字を入力するように促す
        say("4桁の数字を入力してください。")

# ジョブの名前を定義
job_name = "send_message_job"

# スケジューラーの設定とジョブの追加
scheduler = BackgroundScheduler()
scheduler.add_job(send_message, 'cron', hour=14, minute=55, id=job_name)
scheduler.start()

# アプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
