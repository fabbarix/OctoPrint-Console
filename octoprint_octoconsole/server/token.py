from random import choice
from string import ascii_uppercase

ws_token = ''


def token():
    global ws_token

    if not ws_token:
        ws_token = ''.join(choice(ascii_uppercase) for i in range(32))

    return ws_token
