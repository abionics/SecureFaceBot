from database import Database


class Secure:
    min_similarity_coefficient = 0.5

    def __init__(self):
        self.database = Database()
        self.persons = self.database.load()
        print("Loaded", len(self.persons), "values from database")

    def add_person(self, person):
        self.persons.append(person)
        self.database.add_person(person)

    def add_face(self, person, face):
        index = self.persons.index(person.login)
        self.persons[index].add_face(face)
        self.database.update_person(self.persons[index])

    def has_person(self, login):
        return self.persons.__contains__(login)

    def find_face(self, face):
        val, person = min([(person.difference(face), person) for person in self.persons])
        if val < self.min_similarity_coefficient:
            return person
        return None
