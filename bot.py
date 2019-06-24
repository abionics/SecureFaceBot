import logging

import requests


class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)
        self.api_files_url = 'https://api.telegram.org/file/bot{}/'.format(token)
        self.offset = None

    def get_updates(self, timeout=100):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': self.offset}
        resp = requests.get(self.api_url + method, params)
        if resp.json().__contains__('result'):
            result_json = resp.json()['result']
            self.offset = result_json[-1]['update_id'] + 1
            return result_json
        else:
            logging.critical('Response error ' + resp.json().__str__())
            print('Response error' + resp.json().__str__())
            self.delete_webhook()

    def get_file_link(self, file_id, timeout=1000):
        params = {'file_id': file_id, 'timeout': timeout}
        method = 'getFile'
        resp = requests.get(self.api_url + method, params)
        if resp.status_code is not 200:
            return None
        link = resp.json()['result']['file_path']
        return self.api_files_url + link

    def send_message(self, chat_id, text, parse_mode, keyboard):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode, 'reply_markup': keyboard}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp.json()['result']['message_id']

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        method = 'deleteMessage'
        requests.post(self.api_url + method, params)

    def kick(self, chat_id, user_id):
        method = 'kickChatMember'
        params = {'chat_id': chat_id, 'user_id': user_id}
        requests.post(self.api_url + method, params)

    def send_photo(self, chat_id, photo):
        method = 'sendPhoto'
        params = {'chat_id': chat_id, 'photo': photo}
        requests.post(self.api_url + method, params)

    def delete_webhook(self):
        method = 'deleteWebhook'
        requests.post(self.api_url + method)
        logging.warning('Webhook deleted')
