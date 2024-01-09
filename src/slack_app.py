import datetime
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

# メッセージ送信回数のカウンター
message_count = 0

# スケジューリングされたジョブの関数定義
def send_message():
    global message_count
    """Slackチャンネルに定期的なメッセージを送信する。"""
    channel_id = os.environ["SLACK_CHANNEL_ID"]  # メッセージを送信するチャンネルID
    user_id = os.environ["MENTION_USER_ID"]  # メンションするユーザーID
    # メンションを含むメッセージを作成
    message_text = f"<@{user_id}> おはようございます！"
    app.client.chat_postMessage(channel=channel_id, text=message_text)

    # メッセージ送信回数を更新
    message_count += 1

    # 5回送信したらジョブを削除
    if message_count >= 5:
        scheduler.remove_job(job_name)
        message_count = 0  # カウンターをリセット
    else:
        # 1分後に再度この関数を実行するジョブをスケジュール
        next_minute = datetime.datetime.now() + datetime.timedelta(minutes=1)
        scheduler.add_job(send_message, 'date', run_date=next_minute, id=job_name)

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

            # メッセージ送信カウンターをリセット
            message_count = 0

            # 新しい時間でジョブを追加
            start_time = datetime.datetime.now().replace(hour=upper_two_digits, minute=lower_two_digits, second=0)
            scheduler.add_job(send_message, 'date', run_date=start_time, id=job_name)

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

# スケジューラーの初期設定
scheduler = BackgroundScheduler()

# アプリを起動
if __name__ == "__main__":
    scheduler.start()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
