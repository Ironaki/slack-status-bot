import argparse
import os

import requests

SLACK_STATUS_BOT_TOKEN = os.getenv("SLACK_STATUS_BOT_TOKEN")

SLACK_API_URL = "https://slack.com/api"


templates = {
    "clear": {"status_text": "", "status_emoji": ""},
    "afk": {"status_text": "AFK", "status_emoji": ":away:"},
    "vacation": {"status_text": "Vacationing", "status_emoji": ":palm_tree:"},
    "bike": {"status_text": "Biking", "status_emoji": ":bicyclist:"},
}


def get_set_status_req_body(
    status_text: str, status_emoji: str, status_expiration: int
):
    return {
        "profile": {
            "status_text": status_text,
            "status_emoji": status_emoji,
            "status_expiration": status_expiration * 60,
        }
    }


def arg_parser():
    parser = argparse.ArgumentParser(prog="To set Slack status...")
    parser.add_argument("template", choices=templates, nargs="?", default="clear")
    parser.add_argument("-t", "--text", default="")
    parser.add_argument("-e", "--emoji", default="")
    parser.add_argument("-c", "--clear", type=int, default=0)
    return parser.parse_args()


def main():
    parser = arg_parser()
    template = templates[parser.template]
    status_text = template["status_text"]
    status_emoji = template["status_emoji"]
    status_expiration = 0
    if parser.text:
        status_text = parser.text
    if parser.emoji:
        status_emoji = parser.emoji
    if parser.clear:
        status_expiration = parser.clear
    resp = requests.post(
        f"{SLACK_API_URL}/users.profile.set",
        headers={"Authorization": f"Bearer {SLACK_STATUS_BOT_TOKEN}"},
        json=get_set_status_req_body(status_text, status_emoji, status_expiration),
    )
    resp.raise_for_status()
    if not resp.json()["ok"]:
        raise RuntimeError(resp.json()["error"])
    ending_message = "Status Cleared."
    if status_text or status_emoji:
        ending_message = f"Status Set. Text: {status_text}, Emoji: {status_emoji}"
    if status_expiration:
        ending_message = f"{ending_message}, Expire after {status_expiration} minutes."
    print(ending_message)


if __name__ == "__main__":
    main()
