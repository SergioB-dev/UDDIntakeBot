import os
import re
from datetime import datetime

import requests
from flask import Response, json
from requests.structures import CaseInsensitiveDict

EVENTBRITE_HEADER = CaseInsensitiveDict()
EVENTBRITE_HEADER["Connection"] = "keep-alive"
EVENTBRITE_HEADER["Accept-Encoding"] = "gzip, deflate, br"


def sort_orders_by_date(orders):
    # [DATE, FIRSTNAME, LASTNAME, EMAIL]
    sorted_orders = []
    for order in orders:
        order_creation_date = order['created']
        data = [order_creation_date, order['first_name'], order['last_name'], order['email']]
        sorted_orders.append(data)

    sorted_orders.sort(reverse=True, key=lambda date: datetime.strptime(date[0], "%Y-%m-%dT%H:%M:%SZ"))

    return sorted_orders

def prettify(collection):
    results = ''
    index = 1
    for coll in collection:
        results += f'{index}.\t'
        results += f'{coll}'
        results += '\n'
        index += 1
    return results

def prettify_non_ordered(collection):
    results = ''
    for coll in collection:
        results += f'{coll}\n'
    return results

def get_order_from_eventbrite_response(json):
    api_url = json['api_url']
    # Eventbrite URL's look like https://www.eventbriteapi.com/v3/orders/2926608959/
    # We're interested in capturing the 10 digit number
    order_number = re.findall(r'\d{10}', api_url)

    return order_number[0]

def event_brite_get_request(query_item):
        url = f"https://www.eventbriteapi.com/v3/orders/{query_item}"
        response = requests.get(url, headers=EVENTBRITE_HEADER)
        data_response = response.json()

        first_name = data_response['first_name']
        last_name = data_response['last_name']
        full_name = first_name + ' ' +  last_name
        email = data_response['email']
        order_uri = data_response['resource_uri']

        user_msg = prettify_non_ordered([full_name, email, order_uri])

        return user_msg



def get_last_10_events_by_id():
    ORG_ID = os.environ.get('EVENTBRITE_UDD_ORGANIZATION_ID')
    url = f'https://www.eventbriteapi.com/v3/organizations/{ORG_ID}/events/'
    eventbrite_token = os.environ.get('EVENTBRITE_TOKEN')
    EVENTBRITE_HEADER['Authorization'] = f'Bearer {eventbrite_token}'
    print(EVENTBRITE_HEADER)
    response = requests.get(url, headers=EVENTBRITE_HEADER)
    data_response = response.json()

    events = data_response['events']

    events.sort(reverse=True, key= lambda date: datetime.strptime(date['start']['utc'], "%Y-%m-%dT%H:%M:%SZ"))
    return events[0:10]

def background_worker(response_url):
    print("STILL GOING STRONG")
    url='https://www.eventbriteapi.com/v3/organizations/575656201333/events/?time_filter=current_future'
    headers = CaseInsensitiveDict()
    eventbrite_token = os.environ.get('EVENTBRITE_TOKEN')
    headers["Authorization"] = f'Bearer {eventbrite_token}'
    headers["Accept"] = "*/*"
    headers["Connection"] = "keep-alive"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    response = requests.get(url, headers=headers)
    data_response = response.json()
    print('Still running')
    events = data_response['events']
    next_event = events[0]
    next_event_id = next_event['id']

    event_url = f'https://www.eventbriteapi.com/v3/events/{next_event_id}/?expand=ticket_classes'
    response = requests.get(event_url, headers=headers)
    data_response = response.json()
    ticket_classes = data_response['ticket_classes'][0]
    ticket_quantity = ticket_classes['quantity_total']
    tickets_sold = ticket_classes['quantity_sold']
    is_sold_out = ticket_quantity == tickets_sold

    orders_url = f'https://www.eventbriteapi.com/v3/events/{next_event_id}/orders'
    response = requests.get(orders_url, headers=headers)
    data_response = response.json()
    orders = data_response['orders']
    print(*(order for order in orders))
    print(f'{tickets_sold} out of {ticket_quantity} tickets have been sold.')
    reply_string=_prettify_event_orders(orders)
    reply = {'text':reply_string}
    response_header = CaseInsensitiveDict()
    response_header['Content-type'] = 'application/json'
    requests.post(response_url, data=json.dumps(reply), headers=response_header)

def _prettify_event_orders(orders):
    response = ''
    index = 1
    for order in orders:

        first_name=order['first_name']
        last_name=order['last_name']
        email=order['email']
        response += f'{index}. {first_name} {last_name}'
        response += f' | {email}\n'
        index += 1

    return response