import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

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
        text = event.get("text", "")
        channel = event.get("channel")
        
        if channel == DEFAULT_CHANNEL and "hello" in text.lower():
            user = event.get("user")
            say(f"Hello, <@{user}>!")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    send_hello_message()

    handler.start()

if __name__ == "__main__":
    main()