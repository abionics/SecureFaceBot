import json
import sqlite3

from face import Face
from person import Person


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS persons (
                                uid INTEGER NOT NULL,
                                login TEXT UNIQUE NOT NULL,
                                vectors TEXT NOT NULL,
                                weight TEXT NOT NULL,
                                gender TEXT NOT NULL,
                                age DOUBLE NOT NULL,
                                multicultural TEXT NOT NULL)
                            ''')

    def load(self):
        persons = list()
        for row in self.cursor.execute("SELECT * FROM persons"):
            person = self.make_person(row)
            persons.append(person)
        return persons

    @staticmethod
    def make_person(row):
        uid = row[0]
        login = row[1]
        vectors = json.loads(row[2])
        weight = json.loads(row[3])
        gender = row[4]
        age = row[5]
        multicultural = row[6]
        person = Person(uid, login, Face(vectors, (gender, age, multicultural)))
        person.vectors = vectors
        person.weight = weight
        return person

    def add_person(self, person: Person):
        values = self.values_of_person(person)
        self.cursor.execute("INSERT INTO persons VALUES (?,?,?,?,?,?,?)", values)
        self.commit()

    def update_person(self, person):
        values = self.values_of_person(person)
        values.append(person.login)
        self.cursor.execute('''UPDATE persons SET
                                uid=?,
                                login=?,
                                vectors=?,
                                weight=?,
                                gender=?,
                                age=?,
                                multicultural=?
                            WHERE login=?''', values)
        self.commit()

    @staticmethod
    def values_of_person(person):
        vectors = json.dumps(person.vectors)
        weight = json.dumps(person.weight)
        return [person.uid, person.login, vectors, weight, person.gender, person.age, person.multicultural]

    def commit(self):
        self.conn.commit()

    def __del__(self):
        self.conn.close()
