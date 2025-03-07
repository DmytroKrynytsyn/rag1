import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from ..handlers.call_backend import search, embed
from ..utils.slack import get_channel_name_by_id
from ..utils.log import logger

load_dotenv()

def get_attached_text(files: list, slack_app_token) -> str | None:
    if not files:
        logger.info(f"No files attached")
        return None
    
    file = files[0]

    if file.get("filetype") != "text":
        logger.info(f"File type {file.get('filetype')} not supported")
        return None

    file_url = file.get("url_private")
    
    headers = {"Authorization": f"Bearer {slack_app_token}"}
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"File downloaded from {file_url}, length = {len(response.text)}")  
        return response.text
    else:
        return None


def main():
    
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL")

    def send_hello_message():
        app.client.chat_postMessage(channel=DEFAULT_CHANNEL, text="Hello, RAG!")
        logger.info("Hello, RAG!")

    app = App(token=SLACK_BOT_TOKEN)

    @app.event("message")
    def handle_message_events(body, say):
        event = body.get("event", {})
        text: str = event.get("text", "")
        channel_id = event.get("channel")
        datetime = int(float(event.get("ts")))
        channel_name = get_channel_name_by_id(channel_id, app)
        user = event.get("user")

        logger.info(f"handling {text} from {user} in {channel_id}/{channel_name}")
        logger.info(f"event = {event}")
        logger.info(f"body = {body}")
        
        if channel_id == DEFAULT_CHANNEL and "hello" in text.lower():
            say(f"Hello, <@{user}>!")
            return
        
        attached_text = get_attached_text(event.get("files", []), SLACK_BOT_TOKEN)
        if attached_text:
            embed(attached_text, user, datetime, channel_name)
            say(f"{len(attached_text)} characters sent to backend for embedding")
            return
        
        say(f"Searching for answer...")
        answer = search(text, channel_name, False)
        say(f"{answer}")


    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    send_hello_message()

    handler.start()

if __name__ == "__main__":
    main()