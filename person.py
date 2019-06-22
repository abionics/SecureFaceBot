import math

from face import Face


class Person:
    vector_size = 1024
    weight_change = 0.05
    max_property_difference = 0.05

    def __init__(self, uid, login, face: Face):
        self.uid = uid
        self.login = login

        self.vectors = [face.vector]
        self.weight = [1] * self.vector_size

        self.gender = face.gender
        self.age = face.age
        self.multicultural = face.multicultural
        # self.vector = face.vector

    def add(self, face: Face):
        self.vectors.append(face.vector)

    def add_face(self, face: Face):
        self.add(face)
        self.weight_calc()

    def add_faces(self, faces):
        [self.add_face(face) for face in faces]

    def weight_calc(self):
        count = len(self.vectors)
        for i in range(self.vector_size):
            mid_sum = 0.0
            for vector in self.vectors:
                mid_sum += vector[i]
            mid_sum /= count

            max_diff = 0.0
            for vector in self.vectors:
                diff = abs(mid_sum - vector[i])
                if diff > max_diff:
                    max_diff = diff

            if max_diff > self.max_property_difference:
                max_diff = self.max_property_difference
            self.weight[i] = 1.5 * (1.0 - max_diff / self.max_property_difference)

    def difference(self, face):
        min_sum = 100.0
        print(self.login, ' has vectors:', len(self.vectors))
        for vector in self.vectors:
            local_sum = 0
            for i in range(self.vector_size):
                local_sum += self.weight[i] * math.pow(vector[i] - face.vector[i], 2)
            if local_sum < min_sum:
                min_sum = local_sum
            print(self.login, local_sum)
        return min_sum

    def __eq__(self, other):
        return self.login == other
