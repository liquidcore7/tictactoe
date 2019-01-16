from flask import Flask
from flask_restful import Api

from controllers.session import SessionController
from controllers.wakeup import WakeUpHook

app = Flask(__name__)
global_api = Api(app)

global_api.add_resource(SessionController, '/session', endpoint='/session')  # GET
global_api.add_resource(SessionController, '/session/<session_id>', endpoint='/session/<session_id>')  # POST

global_api.add_resource(WakeUpHook, '/wakeup', endpoint='/wakeup')  # GET

if __name__ == '__main__':
    app.run()

