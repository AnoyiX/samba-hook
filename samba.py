import os
import json
import requests
from uuid import uuid4
from dotenv import load_dotenv
from fastlab import logs

load_dotenv()

username = os.getenv('SAMBA_USERNAME')
password = os.getenv('SAMBA_PASSWORD')

if not username or not password:
    raise Exception('SAMBA_USERNAME and SAMBA_PASSWORD must be set in .env')

default_config_path = os.path.expanduser('~/.samba/config.json')
config_path = os.getenv('SAMBA_CONFIG_PATH', default_config_path)

os.makedirs(os.path.dirname(config_path), exist_ok=True)


def _reset_access_token():
    logs.info('start refresh access_token')
    nonce = str(uuid4()).replace('-', '')
    nonce_cookie = {'nonce': nonce}
    state = str(uuid4()).replace('-', '')
    headers = {
        'origin': 'https://cloud.sambanova.ai',
    }
    response = requests.get('https://cloud.sambanova.ai/api/config', cookies=nonce_cookie, headers=headers).json()
    client_id = response['clientId']
    body = {
        'client_id': client_id,
        'username': username,
        'password': password,
        'realm': 'Username-Password-Authentication',
        'credential_type': 'http://auth0.com/oauth/grant-type/password-realm',
    }
    response = requests.post('https://auth0.sambanova.ai/co/authenticate', cookies=nonce_cookie, headers=headers, json=body)
    data = response.json()
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': 'https://cloud.sambanova.ai/web/auth/callback',
        'scope': 'openid profile email',
        'nonce': nonce,
        'connection': 'Username-Password-Authentication',
        'state': state,
        'redirect_path': '/',
        'realm': 'Username-Password-Authentication',
        'login_ticket': data['login_ticket'],
        'auth0Client': 'eyJuYW1lIjoibG9jay5qcyIsInZlcnNpb24iOiIxMi4zLjAiLCJlbnYiOnsiYXV0aDAuanMiOiI5LjIyLjEifX0=',
    }
    cookies = response.cookies.get_dict()
    cookies.update(nonce_cookie)
    response = requests.get('https://auth0.sambanova.ai/authorize', params=params, cookies=cookies, headers=headers)
    access_token = response.history[1].cookies.values()[0]
    logs.info(f'refresh access_token success: {access_token}')
    with open(config_path, 'w+') as f:
        f.seek(0)
        json.dump({
            'access_token': access_token,
        }, f)
        f.truncate()
    return access_token


def _get_access_token():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config['access_token']
    return _reset_access_token()


def llm(body, stream):
    max_retries = 3
    retries = 0
    while retries < max_retries:
        response = requests.post(
            'https://cloud.sambanova.ai/api/completion',
            cookies={
                'access_token': _get_access_token(),
            },
            json={
                'body': body,
                'env_type': 'text',
                'fingerprint': f"anon_{str(uuid4()).replace('-', '')}",
            },
            stream=stream,
        )
        if response.status_code == 401:
            logs.info('access_token expired, try to refresh')
            _reset_access_token()
            retries += 1
            continue
        return response
    return response


_get_access_token()
