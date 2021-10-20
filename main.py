import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import certifi
import sqlite3
import pandas as pd
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from storage_manager import *

import os
import os.path
import ssl
import stat
import subprocess
import sys



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ.get('SIGNING_SECRET'), '/slack/events', app, )
client = WebClient(token=os.environ.get('SLACK_TOKEN'))
BOT_ID = client.api_call('auth.test')['user_id']
logger = logging.getLogger(__name__)

FEEBACK_PROMPT = "Thank you, if you'd like to see anything done differently, please consider leaving some feedback." \
                 "Simply type /suggestion [Your feedback]"  # /Feedback is a resevered slack keyword.



def post_message(msg, channel='#general'):
    client.chat_postMessage(channel=channel, text=msg)


def upload_file(file, channel='C02HYQDP7EZ'):
    try:
        result = client.files_upload(
            channels=channel,
            initial_comments='Testing',
            file=file
        )
        logger.info(result)

    except SlackApiError as e:
        logger.error(f'Error uploading file: {e}')

# SLASH COMMANDS

# Method for uploading csv/pdf/etc. files
@app.route('/get', methods=['POST'])
def get_data():

    data = request.form
    user_input = data.get('text').split(' ')
    user_id = data.get('user_id')               # ID of user who made the request
    # TODO: Add safety checks that all input is received before accessing them on next line
    print(data)
    if user_input[1] == 'csv':              # user_input[1] here should be some data format specified by the user
        convert_db_to_csv()                 # Check and see whether we should update latest working version
        upload_file('output/output.csv', channel=user_id)      # Passing the user id as the channel is essentially a DM
        post_message(FEEBACK_PROMPT, user_id)           # Asking user for feedback in DM

    else:
        pass

    return Response(), 200


@app.route('/add_mentee', methods=['POST'])
def add_member():
    # user_input
    # [0] == first name
    # [1] == last name
    # [2] == email
    data = request.form
    user_input = data.get('text').split(' ')
    # TODO: Add safety checks that all input is received before accessing them on next line

    add_member_to_db(user_input[1].capitalize(), user_input[0].capitalize(), user_input[2], 'Mentee')
    post_message(f'{user_input[0]} has been added to the database as a mentee. ✅')
    print(user_input)
    return Response(), 200

@app.route('/add_mentor', methods=['POST'])
def add_mentor():
    #user_input
    # [0] == first name
    # [1] == last name
    # [2] == email
    data = request.form
    user_input = data.get('text').split(' ')
    # TODO: Add safety checks that all input is received before accessing them on next line

    add_member_to_db(user_input[1].capitalize(), user_input[0].capitalize(), user_input[2], 'Mentor')
    post_message(f'{user_input[0]} has been added to the database as a mentor. ✅')
    return Response(), 200


@app.route('/find', methods=['POST'])
def find_member():

    data = request.form
    search_keyword = data.get('text')
    user_id = data.get('user_id')
    results = search_db(search_keyword)     # List of results
    result_count = len(results)

    # DM the requesting user with the results
    if results:
        post_message(f'We found {result_count} result(s) matching {search_keyword}:\n{results}', channel=user_id)
    else:
        post_message(f'Sorry no results for {search_keyword}.', channel=user_id)

    return Response(), 200








@app.route('/suggestion', methods=['POST'])
def gather_feedback():
    thank_you_text = 'Your feedback has been successfully submitted. ✅\nThank you!'
    date = datetime.now()
    data = request.form
    user_id = data.get('user_id')
    feedback = data.get('text')
    with open('input/feedback.txt', 'a') as txt_file:
        txt_file.write(f'{date}\n')
        txt_file.write(f'{feedback}\n')


    post_message(thank_you_text, channel=user_id)
    print(f'Added feedback:\n {feedback} to input/feedback.txt')

    return Response(), 200

@slack_event_adapter.on("message")      # Responds to any message sent
def message(payload):

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if BOT_ID != user_id:
        post_message(text)

    print("Received")

@slack_event_adapter.on("app_mention")  # Responds to any mentions to the bot directly
def app_mention(event_data):
    print("App mentioned!")
    event = event_data["event"]
    user_id = event_data['user']

    if BOT_ID != user_id:
        client.chat_postMessage(
            channel=event["channel"],
            text=f"You said:\n>{event['text']}",
        )




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=8080,debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
