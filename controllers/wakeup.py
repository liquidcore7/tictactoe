from flask_restful import Resource


# Used to prevent backend from sleeping on heroku
class WakeUpHook(Resource):
    def get(self):
        return '', 200
