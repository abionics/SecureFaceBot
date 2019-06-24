from clarifai.rest import ClarifaiApp

from face import Face


class Recognizer:
    def __init__(self, token):
        self.app = ClarifaiApp(api_key=token)

    def recognize(self, url):
        vector = self.get_face(url)
        about = self.get_meta(url)
        return Face(vector, about)

    def get_face(self, url):
        model = self.app.models.get('d02b4508df58432fbb84e800597b8959')
        response = model.predict_by_url(url)
        region = self.get_region(response)
        if region is None:
            return

        vector = region['data']['embeddings'][0]['vector']
        return vector

    def get_meta(self, url):
        model = self.app.models.get('demographics')
        response = model.predict_by_url(url)
        region = self.get_region(response)
        if region is None:
            return

        about = region['data']['face']
        gender = about['gender_appearance']['concepts'][0]['name']
        age = about['age_appearance']['concepts'][0]['name']
        multicultural = about['multicultural_appearance']['concepts'][0]['name']
        return gender, age, multicultural

    @staticmethod
    def get_region(response):
        data = response['outputs'][0]['data']
        if not data.__contains__('regions'):
            raise Exception('There is no face on image, try again')
        regions = data['regions']
        if len(regions) is not 1:
            raise Exception('You need only one face on image (you have ' + str(len(regions)) + '), try again')
        return regions[0]
