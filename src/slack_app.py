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

# グローバル変数の定義
ALERM_CHANNEL_ID = os.environ["ALERM_CHANNEL_ID"]
ALERM_SETTING_CHANNEL_ID = os.environ["ALERM_SETTING_CHANNEL_ID"]

# スケジューリングされたジョブの関数定義


def send_message():
    channel_id = ALERM_CHANNEL_ID
    user_id = os.environ["MENTION_USER_ID"]  # メンションするユーザーID
    # メンションを含むメッセージを作成
    message_text = f"<@{user_id}> おはようございます！"
    app.client.chat_postMessage(channel=channel_id, text=message_text)

# アプリに対するメンションに応答する関数定義


@app.event("app_mention")
def handle_mention(event, say):
    if event['channel'] == 'C06C3UPM4E8':
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

                # 現在の日時を取得
                now = datetime.datetime.now()
                # 指定された時間で日時オブジェクトを作成
                start_time = now.replace(
                    hour=upper_two_digits, minute=lower_two_digits, second=0)
                # 指定された時間が過去であれば、次の日に設定
                if start_time < now:
                    start_time += datetime.timedelta(days=1)

                # 既存のジョブを削除し、新しいジョブを追加
                if scheduler.get_job(job_name):
                    scheduler.remove_job(job_name)
                # 5回分のジョブを1分間隔で追加
                for i in range(5):
                    run_time = start_time + datetime.timedelta(minutes=i)
                    scheduler.add_job(send_message, 'date',
                                      run_date=run_time, id=f"{job_name}_{i}")

                say(f"設定された時間: {upper_two_digits}時{lower_two_digits}分から5回、1分間隔でメッセージを送信します。")
            else:
                # 条件を満たさない場合のメッセージ
                say("時間は上2桁が0～23、下2桁が0～59の範囲で指定してください。")
        else:
            # 4桁の数字でなければ、4桁の数字を入力するように促す
            say("4桁の数字を入力してください。")

    # 特定のメッセージが含まれているかチェック
    elif event['channel'] == ALERM_CHANNEL_ID:
        # スケジューラーに設定されている全てのジョブを削除
        jobs = scheduler.get_jobs()
        for job in jobs:
            scheduler.remove_job(job.id)
        say("全てのジョブを削除しました。")
        return


# ジョブの名前を定義
job_name = "send_message_job"

# スケジューラーの初期設定
scheduler = BackgroundScheduler()

# アプリを起動
if __name__ == "__main__":
    scheduler.start()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
