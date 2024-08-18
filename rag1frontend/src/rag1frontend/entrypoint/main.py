import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from ..handlers.call_backend import search, embed
from ..utils.slack import get_channel_name_by_id

load_dotenv()

SEARCH_PREFIX = "search:"
DEBUG_SEARCH_PREFIX = "debug search:"
EMBED_PREFIX = "embed:"

def get_attached_test(files: list, slack_app_token) -> str:
    if not files:
        return ""
    
    file = files[0]

    if file.get("filetype") != "text":
        return ""

    file_url = file.get("url_private")
    
    headers = {"Authorization": f"Bearer {slack_app_token}"}
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        return ""

def main():
    
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL")

    def send_hello_message():
        app.client.chat_postMessage(channel=DEFAULT_CHANNEL, text="Hello, RAG!")

    app = App(token=SLACK_BOT_TOKEN)

    @app.event("message")
    def handle_message_events(body, say):
        event = body.get("event", {})
        text: str = event.get("text", "")
        channel_id = event.get("channel")
        timestamp = int(float(event.get("ts")))
        channel_name = get_channel_name_by_id(channel_id, app)

        print(f"handling {text} from {channel_id}/{channel_name}")
        
        if channel_id == DEFAULT_CHANNEL and "hello" in text.lower():
            user = event.get("user")
            say(f"Hello, <@{user}>!")
            return
        
        if text.lower().startswith(SEARCH_PREFIX):
            say(search(text.lower()[len(SEARCH_PREFIX):], channel_name, False))
            return

        if text.lower().startswith(DEBUG_SEARCH_PREFIX):
            say(search(text.lower()[len(DEBUG_SEARCH_PREFIX):], channel_name, True))
            return

        if text.lower().startswith(EMBED_PREFIX):
            text_to_embed = text.lower()[len(EMBED_PREFIX):] + get_attached_test(event.get("files", []), SLACK_BOT_TOKEN)
            say(embed(text_to_embed, user, timestamp, channel_name))
            return

        say(f"Try - searh: ... OR embed: ...")


    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    send_hello_message()

    handler.start()

if __name__ == "__main__":
    main()