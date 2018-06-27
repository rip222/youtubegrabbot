import requests
import json


def getUpdates(offset, token): # returns the list of messages
    getUpdates = 'https://api.telegram.org/bot'+ token + '/getUpdates'
    updates = requests.get(getUpdates + "?offset={}&timeout=60".format(offset), timeout=120)
    data = updates.json()
    messages = data['result']
    return messages


class Sender(object):
    """Sends text message or video when text or youtube link received respectively"""

    def __init__(self, token):
        self.token = token

    def keyboard(self, formats_list):
        keyboard = {'inline_keyboard': [[],[]]}
        mid = int(len(formats_list) / 2)
        for format in formats_list[:mid]:
            dic = {'text': format, 'callback_data': format}
            keyboard['inline_keyboard'][0].append(dic)
        for format in formats_list[mid:]:
            dic = {'text': format, 'callback_data': format}
            keyboard['inline_keyboard'][1].append(dic)
        return "{}".format(json.dumps(keyboard))

    def sendMessage(self, chat_id=None, text=None, reply_markup=None):
        token = self.token
        sendMessage = 'https://api.telegram.org/bot'+ token + '/sendMessage'
        return requests.post(sendMessage, params={'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup})

    def sendVideo (self, chat_id=None, video=None):
        token = self.token
        sendMessage = 'https://api.telegram.org/bot' + token + '/sendVideo'
        return requests.post(sendMessage, params={'chat_id':chat_id}, files={'video': video})
