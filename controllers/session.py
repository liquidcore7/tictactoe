from flask_restful import Resource
from typing import *
from models.state import TicTacToeModel, TicTacToeDelta
from flask import request
from persistance.crud_repository import CrudRepository


class SessionController(Resource):
    Response = Tuple[str, int]

    def __init__(self):
        self.repository: CrudRepository[TicTacToeModel.TicTacToeDTO] = CrudRepository(
            serialize=lambda dto: dto.json(),
            deserialize=lambda json: TicTacToeModel.from_json(json)
        )

    def get(self) -> Response:
        success, session_id = self.repository.create(TicTacToeModel.empty())
        if not success:
            return 'Failed to create session', 500
        return session_id, 200

    def post(self, session_id: str) -> Response:
        maybe_previous_state: Optional[TicTacToeModel.TicTacToeDTO] = self.repository.get(session_id)
        if maybe_previous_state is None:
            return 'Failed to get session state. Is the session outdated?', 500

        # TODO: validate delta
        delta_json: Union[str, dict] = request.get_json(force=True)
        delta = TicTacToeDelta.from_json(delta_json) if type(delta_json) == str else TicTacToeDelta.from_dict(delta_json)
        next_state: TicTacToeModel.TicTacToeDTO = TicTacToeDelta.apply_delta(to=maybe_previous_state, delta=delta)

        updated_status, _ = self.repository.update(session_id, next_state)
        if not updated_status:
            return 'Failed to update session state', 500

        return next_state.json(), 200
