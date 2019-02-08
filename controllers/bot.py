from flask import request
from flask_restful import Resource
from typing import *

from models.state import TicTacToeDelta, TicTacToeModel
from persistance.inject import WithDataBase
from services.bot import BotService


class BotSessionController(Resource):
    def __init__(self):
        self.service = BotService()

    def get(self) -> WithDataBase.Response:
        maybe_session_id: Optional[str] = self.service.create_session()
        if maybe_session_id is None:
            return 'Failed to create bot session', 500
        return maybe_session_id, 200

    def post(self, session_id: str) -> WithDataBase.Response:
        delta_json: Union[str, dict] = request.get_json(force=True)
        delta = TicTacToeDelta.from_json(delta_json) if type(delta_json) == str else TicTacToeDelta.from_dict(delta_json)

        maybe_next_state: Optional[TicTacToeModel.TicTacToeDTO] = self.service.update_session(session_id, delta)
        if maybe_next_state is None:
            return 'Failed to make move', 500
        return maybe_next_state.json(), 200
