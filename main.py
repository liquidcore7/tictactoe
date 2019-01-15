from flask import Flask
from flask_restful import Api

from controllers.dummy import DummyController
from controllers.session import SessionController

app = Flask(__name__)
global_api = Api(app)

global_api.add_resource(SessionController, '/session')  # GET
global_api.add_resource(SessionController, '/session/<session_id: int>')  # POST

global_api.add_resource(DummyController, '/test')  # GET
global_api.add_resource(DummyController, '/test/<data: str>')  # POST

if __name__ == '__main__':
    app.run()

