import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime
from helpers import ratios
from main import app


@app.route('/event', methods=['GET'])
def eventbrite():
    print("Event brite!")
    return Response(), 200