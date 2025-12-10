import os
from uuid import uuid4

import requests
from dotenv import load_dotenv

load_dotenv()

proxy_url = os.getenv('HTTPS_PROXY')

proxies = {
    'http': proxy_url,
    'https': proxy_url,
} if proxy_url else None


def llm(body, api_key, stream):
    env_type = 'text'
    if 'audio' in body.get('model', '').lower():
        env_type = 'audio'
    if 'vision' in body.get('model', '').lower():
        env_type = 'vision'
    body['stream'] = stream
    body['enable_thinking'] = True
    return requests.post(
        'https://cloud.sambanova.ai/api/completion',
        cookies={
            'access_token': api_key,
        },
        json={
            'body': body,
            'env_type': env_type,
            'fingerprint': f"anon_{str(uuid4()).replace('-', '')}",
        },
        stream=stream,
        proxies=proxies
    )
