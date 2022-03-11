import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, request, Response, json
from slackeventsapi import SlackEventAdapter
from datetime import datetime
from helpers import ratios
from flask_httpauth import HTTPTokenAuth
from requests.structures import CaseInsensitiveDict
from search import sort_orders_by_date, prettify, get_order_from_eventbrite_response, event_brite_get_request, get_last_10_events_by_id, background_worker
from channels import SlackChannels
from threading import Thread
from zoom import add_participant_to_db
import psycopg2

from slack_sdk import WebClient



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
auth = HTTPTokenAuth(scheme='Bearer')
eventbrite_token = os.environ.get('EVENTBRITE_TOKEN');
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ.get('SIGNING_SECRET'), '/slack/events', app, )
client = WebClient(token=os.environ.get('SLACK_TOKEN'))
BOT_ID = client.api_call('auth.test')['user_id']
logger = logging.getLogger(__name__)




FEEDBACK_PROMPT = "Thank you, if you'd like to see anything done differently, please consider leaving some feedback." \
                 "Simply type /suggestion [Your feedback]"  # /Feedback is a resevered slack keyword.



def post_message(msg, channel='#slack-eventbrite-brid'):
    print(f'Posting to channel {channel}')
    client.chat_postMessage(channel=channel, text=msg, link_names=1)

# SLASH COMMANDS
@app.route('/find-by-name', methods=['POST'])
def find_member():
    start_time=datetime.now()
    data = request.form
    search_keyword = data.get('text')
    response_url=data.get('response_url')

    try:
        db_connection = psycopg2.connect(
            database=os.environ.get('DATABASE'),
            user='doadmin',
            password=os.environ.get('PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=25060
        )
        cursor=db_connection.cursor()
        sql_query = """SELECT * FROM udd_members WHERE name = %s"""
        cursor.execute(sql_query, (search_keyword,))
        results = cursor.fetchall()
        reply_text=''
        print(results)
        if len(results) > 0:
            for item in results:
                reply_text = 'We found them!\n'
                reply_text += f'- {item}\n'
        else:
            reply_text = f'No {search_keyword} in our database. Make sure the name is spelled correctly.'
        reply = {'text': reply_text}
        response_header = CaseInsensitiveDict()
        response_header['Content-type'] = 'application/json'
        requests.post(response_url, data=json.dumps(reply), headers=response_header)

    except (Exception, psycopg2.Error) as error:
        print('Error fetching data from db', error)
    finally:
        cursor.close()
        db_connection.close()
        print('Closing connection to db')
        return Response(), 200

@app.route('/find-by-email', methods=['POST'])
def find_member_by_email():
    start_time = datetime.now()
    data = request.form
    search_keyword = data.get('text')
    response_url = data.get('response_url')

    try:
        db_connection = psycopg2.connect(
            database=os.environ.get('DATABASE'),
            user='doadmin',
            password=os.environ.get('PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=25060
        )
        cursor = db_connection.cursor()
        sql_query = """SELECT * FROM udd_members WHERE email = %s"""
        cursor.execute(sql_query, (search_keyword,))
        results = cursor.fetchall()
        reply_text = ''
        print(results)
        if len(results) > 0:
            for item in results:
                reply_text = 'We found them!\n'
                reply_text += f'- {item}\n'
        else:
            reply_text = f'No {search_keyword} in our database. Make sure the name is spelled correctly.'
        reply = {'text': reply_text}
        response_header = CaseInsensitiveDict()
        response_header['Content-type'] = 'application/json'
        requests.post(response_url, data=json.dumps(reply), headers=response_header)

    except (Exception, psycopg2.Error) as error:
        print('Error fetching data from db', error)
    finally:
        cursor.close()
        db_connection.close()
        print('Closing connection to db')
        return Response(), 200



    # DM the requesting user with the results
    print('Total time is:', datetime.now() - start_time)

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

    # DM the user
    post_message(thank_you_text, channel=user_id)
    print(f'Added feedback:\n {feedback} to input/feedback.txt')

    return Response(), 200


@app.route('/help', methods=['POST'])
def help():
    data = request.form
    user_id = data.get('user_id')
    message = 'You can find everything you need to know here:\n' \
              'https://github.com/SwiftSergio/UDDIntakeBot/blob/main/README.md \n' \
                'If you still need more help send a message to: @Serg '

    post_message(message, channel=user_id)
    return Response(), 200


# EVENT LISTENERS

# @slack_event_adapter.on("message")      # Responds to any message sent
# def message(payload):
#
#     event = payload.get("event", {})
#     channel_id = event.get("channel")
#     user_id = event.get("user")
#     text = event.get("text")
#
#     if BOT_ID != user_id:
#         post_message(text)
#
#     print("Received")

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



## EVENTBRITE

#  --- WEBHOOKS ---
@app.route('/order-placed', methods=['POST'])
def handle_order_placed():
    response = request.json
    order_number = get_order_from_eventbrite_response(response)
    user_msg = event_brite_get_request(order_number)
    post_message(msg=f'** NEW SIGNUP ON EVENTBRITE **\n {user_msg}', channel=SlackChannels.TESTING_GROUNDS.value)
    return Response(), 200

@app.route('/latest_eventbrite_orders', methods=['POST'])
def dm_user_latest_10_events():
    data = request.form
    user_id = data.get('user_id')
    user_msg = prettify(get_last_10_events_by_id())
    post_message(msg=f'{user_msg}', channel=user_id)
    return Response(), 200

@app.route('/get-latest-eventbrite', methods=['POST'])
def dm_user_latest_eventbrite():
    start_time=datetime.now()

    data = request.form
    print(data)
    # This function will take a while, so return immediately then reply later with our response.
    response_url=data['response_url']
    print(response_url)
    user_id = data.get('user_id')
    print(user_id)
    thr = Thread(target=background_worker, args=[response_url])
    thr.start()
    return {'text': 'This request may take some time..'}, 200

    # Get event specific info, such as tickets sold etc.

    event_url=f'https://www.eventbriteapi.com/v3/events/{next_event_id}/?expand=ticket_classes'
    response = requests.get(event_url, headers=headers)
    data_response = response.json()
    ticket_classes=data_response['ticket_classes'][0]
    ticket_quantity=ticket_classes['quantity_total']
    tickets_sold=ticket_classes['quantity_sold']
    is_sold_out=ticket_quantity==tickets_sold

    # Get orders for an event
    try: # SLACK GIVES US 3000 MS TO Reply with a response, but we need more time, so reply but keep working
        print('TRY TIME',datetime.now() - start_time)
        return Response(), 200
    finally:
        orders_url=f'https://www.eventbriteapi.com/v3/events/{next_event_id}/orders'
        response = requests.get(orders_url, headers=headers)
        data_response=response.json()
        orders=data_response['orders']
        print(*(order for order in orders))
        print(f'{tickets_sold} out of {ticket_quantity} tickets have been sold.')
        print("FINALLY TIME", datetime.now() - start_time)





    return Response(), 200



@app.route('/eventbrite', methods=['POST'])
def dm_user_list_of_event_brite():
    data = request.form
    user_id = data.get('user_id')
    event_id = os.environ.get('UDD_INTAKE_EVENT_ID')
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/orders"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f'Bearer {eventbrite_token}'
    headers["Accept"] = "*/*"
    headers["Connection"] = "keep-alive"
    headers["Accept-Encoding"] = "gzip, deflate, br"

    response = requests.get(url, headers=headers)
    data_response = response.json()
    orders = data_response['orders']
    sorted_orders = sort_orders_by_date(orders)
    user_msg = prettify(sorted_orders)
    post_message(f'Latest EventBrite Signups: \n{user_msg}', channel=user_id)
    return Response(), 200
    

@app.route('/get-latest-eventbrite', methods=['POST'])
def get_latest_event_order():
   pass

@app.route('/zoom-participant-joined', methods=['POST'])
def handle_zoom_participant_joining():
    print(request.json)
    answer = request.json
    payload = answer['payload']
    print(payload)
    meeting = payload['object']
    participant = meeting['participant']
    user_name = participant['user_name']
    id = participant['id']
    email = participant['email']

    add_participant_to_db(user_name, email)

    return Response(), 200

@app.route('/db-update', methods=['POST'])
def notify_of_db_update():
    #res = request.get_json()
    #print(res)
    if request.is_json:
        res = request.json
        index = 1
        for msg in res['members']:
            numbered_msg=f'{index}. ' + msg
            post_message(msg=numbered_msg, channel=SlackChannels.TESTING_GROUNDS.value)
            index += 1
        print(res)
    else:
        print('NOT JSON')
    return Response(), 200

@app.route('/webtest', methods=['POST'])
def get_stuff():
    this = request.form
    print(this)
    return Response(), 200

@app.route('/testevent', methods=['POST'])
def test_event():
    event_id=os.environ.get('UDD_INTAKE_EVENT_ID')
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/orders"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f'Bearer {eventbrite_token}'
    headers["Accept"] = "*/*"
    headers["Connection"] = "keep-alive"
    headers["Accept-Encoding"] = "gzip, deflate, br"

    response = requests.get(url,headers=headers)
    data_response = response.json()
    orders = data_response['orders']
    sorted_orders = sort_orders_by_date(orders)
    print(sorted_orders)
    print(response.status_code)
    post_message(f'WE HAVE THE FOLLOWING USERS SIGNED UP: {sorted_orders}', channel=SlackChannels.TESTING_GROUNDS.name)
    return Response(), 200




if __name__ == '__main__':
    # get_all_users()
    app.run(port=8080,debug=True)

