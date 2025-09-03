import os
from uuid import uuid4

import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('SAMBA_TOKEN')
token_api = os.getenv('SAMBA_TOKEN_API')
proxy_url = os.getenv('HTTPS_PROXY')

proxies = {
    'http': proxy_url,
    'https': proxy_url,
} if proxy_url else None


def llm(body, stream):
    env_type = 'text'
    if 'audio' in body.get('model', '').lower():
        env_type = 'audio'
    if 'vision' in body.get('model', '').lower():
        env_type = 'vision'
    body['stream'] = stream
    body['enable_thinking'] = True
    _token = token
    if token_api:
        _token = requests.get(token_api).text
    return requests.post(
        'https://cloud.sambanova.ai/api/completion',
        cookies={
            'access_token': _token,
        },
        json={
            'body': body,
            'env_type': env_type,
            'fingerprint': f"anon_{str(uuid4()).replace('-', '')}",
        },
        stream=stream,
        proxies=proxies
    )
