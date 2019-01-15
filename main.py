from flask import Flask
from flask_restful import Api

from controllers.session import SessionController

app = Flask(__name__)
global_api = Api(app)

global_api.add_resource(SessionController, '/session', endpoint='/session')  # GET
global_api.add_resource(SessionController, '/session/<session_id>', endpoint='/session/<session_id>')  # POST

if __name__ == '__main__':
    app.run()

