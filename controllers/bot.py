from flask_restful import Resource
from typing import *

from models.state import TicTacToeModel
from persistance.inject import WithDataBase


class BotController(Resource, WithDataBase[TicTacToeModel.TicTacToeDTO]):

    def __init__(self):
        super().__init__(lambda dto: dto.json(), lambda string: TicTacToeModel.from_json(string))

    def post(self, session_id: str) -> super().Response:
        maybe_previous_state: Optional[TicTacToeModel.TicTacToeDTO] = self.db.get(session_id)
        if maybe_previous_state is None:
            return 'Failed to get session state. Is the session outdated?', 500

        return 'Not implemented', 404

