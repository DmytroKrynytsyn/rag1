from slack_bolt import App

def get_channel_name_by_id(channel_id: str, app: App):
    try:
        # Call conversations.info to get the channel info
        result = app.client.conversations_info(channel=channel_id)
        # Extract and return the channel name
        return result['channel']['name']
    except Exception as e:
        print(f"Error fetching channel name: {e}")
        return None