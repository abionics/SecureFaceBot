import logging

from bot import Bot
from person import Person
from recognizer import Recognizer


class Controller:
    sign_up_init_status = '*sign_up_init*'
    sign_up_login_status = '*sign_up_login*'
    sign_in_init_status = '*sign_in_init*'
    sign_in_login_status = '*sign_in_login*'
    singed_in_status = '*singed_in*'
    add_photo_status = '*add_photo*'

    def __init__(self, clarifai_token, telegram_token):
        self.recognizer = Recognizer(clarifai_token)
        self.bot = Bot(telegram_token)
        self.persons = list()
        self.users = dict()

    def start(self):
        offset = None

        while True:
            self.bot.get_updates(offset)
            data = self.bot.get_last_update()
            if data == '':
                continue
            last_update_id = data['update_id']
            offset = last_update_id + 1

            user = self.get(data, ['message', 'from', 'id'])
            chat = self.get(data, ['message', 'chat', 'id'])
            text = self.get(data, ['message', 'text'])
            photos = self.get(data, ['message', 'photo'])

            if (user is None) or (chat is None):
                logging.error('No from_id or no chat_id (from_id: ' + str(user) + ', chat_id: ' + str(chat) + ')')  # todo
            elif user != chat:
                self.bot.send_message(chat, 'I work only in private chats')  # todo
                logging.warning('This message was not in private chat (from_id: ' + str(user) + ')')
            else:
                if (text is not None) and (text.lower() == 'exit'):
                    self.users[user] = None
                    continue
                status = self.users.get(user)
                if status is not None:
                    status, login = status
                    print(status, login)
                    if (status == self.sign_up_init_status) and (text is not None):
                        self.sign_up_login(user, text)
                    elif (status == self.sign_up_login_status) and (photos is not None):
                        self.sign_up_confirm(user, photos)
                    elif (status == self.sign_in_init_status) and (text is not None):
                        self.sign_in_login(user, text)
                    elif (status == self.sign_in_login_status) and (photos is not None):
                        self.sign_in_confirm(user, photos)
                    elif (status == self.singed_in_status) and (text is not None) and (text.lower() == "add photo"):
                        self.add_photo_init(user)
                    elif (status == self.add_photo_status) and (photos is not None):
                        self.add_photo(user, photos)
                elif text is not None:
                    command = text.lower()
                    if (command == 'register') or (command == 'sign up'):
                        self.sign_up_init(user)
                    elif (command == 'login') or (command == 'sign in') or (command == 'log in'):
                        self.sign_in_init(user)

    def sign_up_init(self, user):
        self.users[user] = (self.sign_up_init_status, '')
        self.send_message(user, 'Enter your unique login (or type "exit" to go back)')

    def sign_up_login(self, user, text):
        if text.lower() == "exit":
            self.users[user] = None
            return
        if self.persons.__contains__(text):
            self.send_message(user, 'This login is already taken, enter another (or type "exit" to go back)')
            return
        self.users[user] = (self.sign_up_login_status, text)
        self.send_message(user, 'Send your photo (or type "exit" to go back)')

    def sign_up_confirm(self, user, photos):
        login = self.users[user][1]
        link = self.get_photo_link(user, photos)
        face = self.recognizer.recognize(link)
        person = Person(user, login, face)
        self.persons.append(person)
        self.send_message(user, 'Account created!')
        self.users[user] = (self.singed_in_status, login)

    def sign_in_init(self, user):
        self.users[user] = (self.sign_in_init_status, '')
        self.send_message(user, 'Enter your login (or type "exit" to go back)')

    def sign_in_login(self, user, text):
        if not self.persons.__contains__(text):
            self.send_message(user, 'This login is not in our database, try again (or type "exit" to go back)')
            return
        self.users[user] = (self.sign_in_login_status, text)
        self.send_message(user, 'Confirm by your photo (or type "exit" to go back)')

    def sign_in_confirm(self, user, photos):
        try:
            login = self.users[user][1]
            link = self.get_photo_link(user, photos)
            face = self.recognizer.recognize(link)
            self.find_face(face)
            self.users[user] = (self.singed_in_status, login)
        except Exception as error:
            self.send_message(user, error.__str__())

    def add_photo_init(self, user):
        login = self.users[user][1]
        self.users[user] = (self.add_photo_status, login)
        self.send_message(user, 'Send your photo (or type "exit" to go back)')

    def add_photo(self, user, photos):
        login = self.users[user][1]
        link = self.get_photo_link(user, photos)
        face = self.recognizer.recognize(link)
        index = self.persons.index(login)
        self.persons[index].add_face(face)

    def find_face(self, face):
        for person in self.persons:
            val = person.difference(face)
            print(person.login, val)

    def get_photo_link(self, user, photos):
        self.send_message(user, '...')
        if (photos is None) or (len(photos) is 0):
            self.send_message(user, 'No photo in this message, try again (or type "exit" to go back)')
            return
        photo = photos[-1]
        photo_id = photo['file_id']
        link = self.bot.get_file_link(photo_id)
        if link is None:
            self.send_message(user, 'Photo cannot be loaded, try again (or type "exit" to go back)')
            return
        return link

    def send_message(self, user, text):
        self.bot.send_message(user, text)
        header = '[user ' + str(user) + ']: Message: '
        logging.info(header + text)

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
