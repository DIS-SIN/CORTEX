import json
import requests


HDRS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def send_to_app(context, service, data):
    response = requests.post(
        '%s/%s' % (context.app_uri, service),
        headers=HDRS,
        data=data
    )
    return response.json()
