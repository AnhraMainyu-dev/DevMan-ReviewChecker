import time

import requests
from decouple import config


def notify_to_tg(tg_channel_id, tg_bot_token, text):
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    response = requests.post(url, data={"chat_id": tg_channel_id, "text": text})
    response.raise_for_status()


def main():
    devman_token = config("DEVMAN_TOKEN")
    tg_bot_token = config("TG_BOT_TOKEN")
    tg_user_id = config("TG_USER_ID")

    url = "https://dvmn.org/api/long_polling/"
    headers = {
        "Authorization": f"Token {devman_token}",
    }

    timestamp = None

    while True:
        try:
            params = {"timestamp": timestamp}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            lessons_review = response.json()
            if lessons_review["status"] == "timeout":
                timestamp = lessons_review["timestamp_to_request"]
            else:
                timestamp = lessons_review["last_attempt_timestamp"]
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue

        if lessons_review["status"] == "found":
            for attempt in lessons_review["new_attempts"]:
                if attempt["is_negative"]:
                    result = "К сожалению в уроке нашлись ошибки, переделывай"
                else:
                    result = "Всё гут, давай дальше"
                text = (
                    f"Преподаватель проверил урок {attempt['lesson_title']}\n"
                    f"Ссылка на урок - {attempt['lesson_url']}\n"
                    f"{result}"
                )
                notify_to_tg(tg_user_id, tg_bot_token, text)


if __name__ == "__main__":
    main()
