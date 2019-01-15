from flask import Flask
from flask_restful import Api

from controllers.dummy import DummyController
from controllers.session import SessionController

app = Flask(__name__)
global_api = Api(app)

global_api.add_resource(SessionController, '/session', endpoint='/session')  # GET
global_api.add_resource(SessionController, '/session/<session_id>', endpoint='/session/<session_id>')  # POST

global_api.add_resource(DummyController, '/test', endpoint='/test')  # GET
global_api.add_resource(DummyController, '/test/<data>', endpoint='/test/<data>')  # POST

if __name__ == '__main__':
    app.run()

