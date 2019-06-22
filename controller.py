import json
import logging

from bot import Bot
from person import Person
from recognizer import Recognizer
from secure import Secure


class Controller:
    owner_id = 433518097
    about_app = 'Hello! Secure Face bot can grant you access to you private data from any phone via only your photo!' \
                '\nSign up once if you dont have account' \
                '\nSign in if you already have account'

    sign_up_login_status = '*sign_up_login*'
    sign_up_photo_status = '*sign_up_photo*'
    sign_in_status = '*sign_in*'
    signed_in_status = '*singed_in*'
    add_photo_status = '*add_photo*'

    def __init__(self, clarifai_token, telegram_token):
        self.recognizer = Recognizer(clarifai_token)
        self.bot = Bot(telegram_token)
        self.secure = Secure()
        self.users_status = dict()
        self.users_login = dict()
        self.users_message = dict()

    def start(self):
        offset = None

        while True:
            self.bot.get_updates(offset)
            data = self.bot.get_last_update()
            if data == '':
                continue
            last_update_id = data['update_id']
            offset = last_update_id + 1

            print(data)

            mid = self.get(data, ['message', 'message_id'])
            user = self.get(data, ['message', 'from', 'id'])
            chat = self.get(data, ['message', 'chat', 'id'])
            text = self.get(data, ['message', 'text'])
            photos = self.get(data, ['message', 'photo'])

            if user is None:  # button pressed (callback query)
                user = self.get(data, ['callback_query', 'from', 'id'])
                chat = self.get(data, ['callback_query', 'from', 'id'])
                text = self.get(data, ['callback_query', 'data'])

            if (user is None) or (chat is None):
                logging.error('No from_id or no chat_id (from_id: ' + str(user) + ', chat_id: ' + str(chat) + ')')
            elif user != chat:
                self.send(chat, 'I work only in private chats')
            else:
                if mid is not None:
                    self.bot.delete_message(user, mid)
                self.message(user, text, photos)

    def message(self, user, text, photos):
        self.commands(user, text)
        status = self.users_status.get(user)
        if status is None:
            self.startup(user, text)
        elif status == self.sign_up_login_status:
            self.sign_up_login(user, text)
        elif status == self.sign_up_photo_status:
            self.sign_up_photo(user, text, photos)
        elif status == self.sign_in_status:
            self.sign_in(user, text, photos)
        elif status == self.signed_in_status:
            self.profile(user, text)
        elif status == self.add_photo_status:
            self.add_photo(user, text, photos)

    def startup(self, user, text):
        if text is not None:
            text = text.lower()
        if text == 'sign up':
            keyboard = self.make_keyboard(['Cancel'])
            self.send(user, 'Enter your login', keyboard)
            self.users_status[user] = self.sign_up_login_status
        elif (text == 'sign in') or (text == 'log in') or (text == 'login'):
            keyboard = self.make_keyboard(['Cancel'])
            self.send(user, 'Send your face', keyboard)
            self.users_status[user] = self.sign_in_status
        else:
            keyboard = self.make_keyboard(['Sign in', 'Sign up'])
            self.send(user, self.about_app, keyboard)

    def sign_up_login(self, user, text):
        keyboard = self.make_keyboard(['Cancel'])
        if (text == 'Cancel') or (text == 'cancel'):
            self.users_status[user] = None
            self.users_login[user] = None
            self.startup(user, '')
        elif text is None:
            self.send(user, "Please, enter your login", keyboard)
        elif self.secure.has_person(text):
            self.send(user, 'This login is already taken, enter another', keyboard)
        else:
            self.send(user, "Send your face", keyboard)
            self.users_status[user] = self.sign_up_photo_status
            self.users_login[user] = text

    def sign_up_photo(self, user, text, photos):
        keyboard = self.make_keyboard(['Cancel'])
        if (text == 'Cancel') or (text == 'cancel'):
            self.users_status[user] = None
            self.users_login[user] = None
            self.startup(user, '')
        elif photos is None:
            self.send(user, "Please, send your face", keyboard)
        else:
            try:
                login = self.users_login[user]
                link = self.get_photo_link(user, photos)
                face = self.recognizer.recognize(link)
                person = Person(user, login, face)
                self.secure.add_person(person)
                self.users_status[user] = self.sign_in_status
                self.send(user, 'Account created!')
            except Exception as error:
                self.send(user, error.__str__(), keyboard)

    def sign_in(self, user, text, photos):
        keyboard = self.make_keyboard(['Cancel'])
        if (text == 'Cancel') or (text == 'cancel'):
            self.users_status[user] = None
            self.users_login[user] = None
            self.startup(user, '')
        elif photos is None:
            self.send(user, "Please, send your photo", keyboard)
        else:
            try:
                link = self.get_photo_link(user, photos)
                face = self.recognizer.recognize(link)
                person = self.secure.find_face(face)
                if person is None:
                    self.send(user, 'Cannot define profile by this photo, please try again', keyboard)
                else:
                    self.users_status[user] = self.signed_in_status
                    self.users_login[user] = person.login
                    self.send(user, 'Login as ' + person.login)
                    self.profile(user, '')
            except Exception as error:
                self.send(user, error.__str__(), keyboard)

    def profile(self, user, text):
        if text is not None:
            text = text.lower()
        if (text == 'exit') or (text == 'log out'):
            self.users_status[user] = None
            self.users_login[user] = None
            self.startup(user, '')
        elif text == 'add photo':
            keyboard = self.make_keyboard(['Cancel'])
            self.users_status[user] = self.add_photo_status
            self.send(user, 'Send your photo', keyboard)
        else:
            keyboard = self.make_keyboard(['Enter secret', 'Add photo', 'Exit'])
            login = self.users_login[user]
            self.send(user, 'Welcome ' + login + '\nSome info', keyboard)

    def add_photo(self, user, text, photos):
        keyboard = self.make_keyboard(['Cancel'])
        if (text == 'Cancel') or (text == 'cancel'):
            self.users_status[user] = None
            self.users_login[user] = None
            self.profile(user, '')
        elif photos is None:
            self.send(user, "Please, send your photo", keyboard)
        else:
            try:
                link = self.get_photo_link(user, photos)
                face = self.recognizer.recognize(link)
                login = self.users_login[user]
                self.secure.add_face(login, face)
                self.users_status[user] = self.signed_in_status
                self.send(user, 'Photo successfully added')
                self.profile(user, '')
            except Exception as error:
                self.send(user, error.__str__(), keyboard)

    def send(self, user, text, keyboard=None):
        last = self.users_message.get(user)
        if last is not None:
            self.bot.delete_message(user, last)
        last = self.bot.send_message(user, text, keyboard)
        self.users_message[user] = last

    def get_photo_link(self, user, photos):
        self.send(user, 'Loading...')
        if (photos is None) or (len(photos) is 0):
            raise Exception("No photo in this message, try again")
        photo = photos[-1]
        photo_id = photo['file_id']
        link = self.bot.get_file_link(photo_id)
        if link is None:
            raise Exception('Photo cannot be loaded, try again')
        return link

    def commands(self, user, text):
        if (text is None) or (user is None):
            return
        text = text.lower()
        if user == self.owner_id:
            if text == 'log out all':
                for u, status in self.users_status.items():
                    if status is not None:
                        if status == self.signed_in_status:
                            self.message(u, 'exit', None)
                        else:
                            self.message(u, 'cancel', None)
                        self.users_status[u] = None
                        self.users_login[u] = None
                        self.users_message[u] = None
            if text == 'stop':
                for u, status in self.users_status.items():
                    if status is not None:
                        if status == self.signed_in_status:
                            self.message(u, 'exit', None)
                        else:
                            self.message(u, 'cancel', None)
                exit(0)

    @staticmethod
    def make_keyboard(texts):
        buttons = list()
        [buttons.append([{'text': text, 'callback_data': text}]) for text in texts]
        return json.dumps({'inline_keyboard': buttons})

    @staticmethod
    def get(data, keys):
        if data.__contains__(keys[0]):
            first = keys[0]
            if len(keys) is 1:
                return data[first]
            else:
                keys.pop(0)
                return Controller.get(data[first], keys)
        else:
            return None
