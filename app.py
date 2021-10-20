import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from gevent.pywsgi import WSGIServer



from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ.get('SIGNING_SECRET'), '/slack/events', app)
app.run(host='0.0.0.0',port=8080,debug=True)

client = WebClient(token=os.environ.get('SLACK_TOKEN'))

# @app.route('/slack/events')
# def hello_world():
#     return 'Hello'


def post_message(msg):
    client.chat_postMessage(channel='#general', text=msg)


@slack_event_adapter.on("message")
def message(payload):

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    post_message(text)

    print("Received")



    client.chat_postMessage(channel=channel_id, text='Hello!')


@slack_events_adapter.on("app_mention")
def handle_mentions(event_data):
    print("App mentioned!")
    event = event_data["event"]
    client.chat_postMessage(
        channel=event["channel"],
        text=f"You said:\n>{event['text']}",
    )

logger = logging.getLogger(__name__)


def fetch_conversations():
    try:
        result = client.conversations_list()
        print(result)
    except SlackApiError as e:
        logger.error("Error fetching conversations: {}".format(e))


def find_conversation():
    try:
        for response in client.conversations_list():
            for channel in response['channels']:
                print(channel['name'])
    except SlackApiError as e:
        print(f'Error {e}')


find_conversation()


# post_message('Hello there!')

# fetch_conversations()


    # Main Token
# xapp-1-A02JRDMLALQ-2613799899234-18a3b0924375b1c80c935c92868d5ba5eab49119753b186bf9189f805a89fa4a