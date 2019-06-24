import logging

from database import Database


class Secure:
    min_similarity_coefficient = 0.5

    def __init__(self):
        self.database = Database()
        self.persons = self.database.load()
        print('Loaded', len(self.persons), 'values from database')
        logging.info('Loaded' + str(len(self.persons)) + 'values from database')

    def add_person(self, person):
        self.persons.append(person)
        self.database.add_person(person)

    def add_face(self, login, face, log_user):  # log_user only for logging
        index = self.persons.index(login)
        person = self.persons[index]
        diff = person.difference(face, log_user)
        person.add_face(face)
        self.database.update_person(person)
        return diff

    def has_person(self, login):
        return self.persons.__contains__(login)

    def find_face(self, face, log_user):  # log_user only for logging
        val, person = min([(person.difference(face, log_user), person) for person in self.persons])
        if val < self.min_similarity_coefficient:
            return person
        return None
