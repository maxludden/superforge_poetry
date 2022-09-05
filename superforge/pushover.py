import os
from json import loads

import requests
from requests import get, post, Response
from pprint import pprint

from dotenv import dotenv_values

secret_dict = dotenv_values("env/.env")
USER_KEY = secret_dict["USER_KEY"]
APP_TOKEN = secret_dict["API_TOKEN"]


def pushover(title: str, msg: str):
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "title": title,
        "message": msg,
    }
    response = post(url, data=payload)
    if response.status_code == 200:
        result = loads(response.text)
        pprint(result)


