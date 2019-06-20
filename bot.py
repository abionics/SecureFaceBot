import logging

import requests


class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.api_files_url = "https://api.telegram.org/file/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=100):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        if resp.json().__contains__('result'):
            result_json = resp.json()['result']
            return result_json
        else:
            logging.critical("Response error " + resp.json().__str__())
            print("Response error" + resp.json().__str__())
            self.delete_webhook()

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            try:
                last_update = get_result[len(get_result)]
            except Exception:
                print('last_update index out of range')
                last_update = ''
        return last_update

    def get_file_link(self, file_id, timeout=1000):
        params = {'file_id': file_id, 'timeout': timeout}
        method = 'getFile'
        resp = requests.get(self.api_url + method, params)
        if resp.status_code is not 200:
            return None
        link = resp.json()["result"]["file_path"]
        return self.api_files_url + link

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def kick(self, chat_id, user_id):
        method = 'kickChatMember'
        params = {'chat_id': chat_id, 'user_id': user_id}
        resp = requests.get(self.api_url + method, params)
        print('kicked:', resp)

    def send_photo(self, chat_id, photo):
        method = 'sendPhoto'
        params = {'chat_id': chat_id, 'photo': photo}
        resp = requests.get(self.api_url + method, params)
        print('send photo:', resp)

    def delete_webhook(self):
        method = 'deleteWebhook'
        requests.post(self.api_url + method)
        logging.warning("Webhook deleted")
