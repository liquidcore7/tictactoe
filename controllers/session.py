from flask_restful import Resource
from typing import *
from models.state import TicTacToeModel, TicTacToeDelta
from flask import request
from services.session import SessionService


class SessionController(Resource):

    def __init__(self):
        self.service = SessionService()

    def get(self) -> super().Response:
        maybe_session_id: Optional[str] = self.service.create_session()
        if maybe_session_id is None:
            return 'Failed to create session', 500
        return maybe_session_id, 200

    def post(self, session_id: str) -> super().Response:
        delta_json: Union[str, dict] = request.get_json(force=True)
        delta = TicTacToeDelta.from_json(delta_json) if type(delta_json) == str else TicTacToeDelta.from_dict(delta_json)

        maybe_next_state: Optional[TicTacToeModel.TicTacToeDTO] = self.service.update_session(session_id, delta)
        if maybe_next_state is None:
            return 'Failed to update session state', 500
        return maybe_next_state.json(), 200
