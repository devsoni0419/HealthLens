import time
import threading
from datetime import datetime
import requests

PUSHOVER_USER_KEY = "uz6r56xtfgq3tg84ti74udbj6dieq2"
PUSHOVER_API_TOKEN = "a6gckz7c7j1kytnxy1y1t2eatjtb3g"


def send_notification(message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message
        }
    )


def set_reminder(message, date_str, time_str):
    try:
        target_datetime = datetime.strptime(
            f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
        )

        delay = (target_datetime - datetime.now()).total_seconds()

        if delay <= 0:
            return "❌ Time already passed"

        def task():
            time.sleep(delay)
            send_notification(message)

        threading.Thread(target=task, daemon=True).start()

        return f"✅ Reminder set for {target_datetime}"

    except Exception as e:
        return f"❌ Error: {str(e)}"