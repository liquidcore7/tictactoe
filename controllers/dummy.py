from flask_restful import Resource


class DummyController(Resource):

    def get(self):
        return 'Dummy version', 200

    def post(self, data: str):
        return data, 200
