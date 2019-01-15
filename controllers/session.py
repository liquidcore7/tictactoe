from flask_restful import Resource, reqparse
from typing import *
from models.state import TicTacToeModel, TicTacToeDelta


class SessionController(Resource):
    def __init__(self, max_session: int=1500):
        self.activeSessions: Dict[int, TicTacToeModel.TicTacToeDTO] = dict()
        self.availableIds: Set[int] = set(range(max_session))
        self.stateParser = reqparse.RequestParser()\
            .add_argument('player', type=str)\
            .add_argument('updated_field', type=int)

    def __new_session__(self) -> Optional[int]:
        if len(self.availableIds) > 0:
            sess_id: int = self.availableIds.pop()
            self.activeSessions[sess_id] = TicTacToeModel.empty()
            return sess_id
        return None

    def __end_session__(self, sess_id: int) -> None:
        del self.activeSessions[sess_id]
        self.availableIds.add(sess_id)

    def get(self) -> Tuple[Union[str, int], int]:
        maybe_id: Optional[int] = self.__new_session__()
        if not maybe_id:
            return 'Failed to create session', 500
        return maybe_id, 200

    def post(self, session_id: int):
        # TODO: add error handling
        previous_state: TicTacToeModel.TicTacToeDTO = self.activeSessions[session_id]
        delta = TicTacToeDelta.from_dict(self.stateParser.parse_args())
        next_state: TicTacToeModel.TicTacToeDTO = TicTacToeDelta.apply_delta(to=previous_state, delta=delta)
        self.activeSessions[session_id] = next_state
        return next_state.json(), 200
