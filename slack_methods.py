from slack_sdk import WebClient
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = WebClient(token=os.environ.get('SLACK_TOKEN'))

def get_all_users():
    result = client.users_list()
    for r in result['members']:
        if not r['is_bot']:
            print(r)