import json
from requests import request

from configs import SERVER_URL, CREDENTIALS_PATH
from API_paths import LOGIN_PATH


def authenticate():
  url = SERVER_URL + LOGIN_PATH
  with open(CREDENTIALS_PATH) as f:
    credentials = json.load(f)
  params = credentials
  result = request(url=url, method='POST', json=params, verify=False).json()
  return result['token']