import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

from ..handlers.call_backend import search, embed
from ..utils.slack import get_channel_name_by_id

load_dotenv()

def main():
    
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL")

    def send_hello_message():
        app.client.chat_postMessage(channel=DEFAULT_CHANNEL, text="Hello, RAG!")
        app.client.chat_postMessage(channel="C07J0GW6E3S", text="Hello, RAG!")


    app = App(token=SLACK_BOT_TOKEN)

    @app.event("message")
    def handle_message_events(body, say):
        event = body.get("event", {})
        text: str = event.get("text", "")
        channel_id = event.get("channel")

        print(f"handling {text} from {channel_id}/{get_channel_name_by_id(channel_id, app)}")
        
        if channel_id == DEFAULT_CHANNEL and "hello" in text.lower():
            user = event.get("user")
            say(f"Hello, <@{user}>!")
            return
        
        channel_name = get_channel_name_by_id(channel_id, app)

        if text.lower().startswith("search:"):
            say(search(text.lower(), channel_name))

        if text.lower().startswith("embed:"):
            say(embed(text.lower(), channel_name))

        say(f"Try - searh: ... OR embed: ...")


    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    send_hello_message()

    handler.start()

if __name__ == "__main__":
    main()