import os
from uuid import uuid4

import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('SAMBA_TOKEN')

if not token :
    raise Exception('SAMBA_TOKEN must be set in .env')

def llm(body, stream):
    env_type = 'text'
    if 'audio' in body.get('model', '').lower():
        env_type = 'audio'
    if 'vision' in body.get('model', '').lower():
        env_type = 'vision'
    body['stream'] = stream
    return requests.post(
        'https://cloud.sambanova.ai/api/completion',
        cookies={
            'access_token': token,
        },
        json={
            'body': body,
            'env_type': env_type,
            'fingerprint': f"anon_{str(uuid4()).replace('-', '')}",
        },
        stream=stream,
    )
