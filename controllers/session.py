from flask_restful import Resource
from typing import *
from models.state import TicTacToeModel, TicTacToeDelta
from flask import request
from models.state import TicTacToeHelper as players


class SessionState:
    def __init__(self, max_session: int=1500):
        self.activeSessions: Dict[int, TicTacToeModel.TicTacToeDTO] = dict()
        self.availableIds: Set[int] = set(range(max_session))

    def new_session(self) -> Optional[int]:
        if len(self.availableIds) > 0:
            sess_id: int = self.availableIds.pop()
            self.activeSessions[sess_id] = TicTacToeModel.empty()
            return sess_id
        return None

    def end_session(self, sess_id: int) -> None:
        del self.activeSessions[sess_id]
        self.availableIds.add(sess_id)

    def get_session(self, sess_id: int) -> TicTacToeModel.TicTacToeDTO:
        return self.activeSessions[sess_id]

    def update_session(self, sess_id: int, new_state: TicTacToeModel.TicTacToeDTO):
        if new_state.winner != players.Players.FREE:
            self.end_session(sess_id)
        else:
            self.activeSessions[sess_id] = new_state


GlobalSessionState = SessionState()


class SessionController(Resource):

    def get(self) -> Tuple[Union[str, int], int]:
        maybe_id: Optional[int] = GlobalSessionState.new_session()
        if maybe_id is None:
            return 'Failed to create session', 500
        return maybe_id, 200

    def post(self, session_id: int):
        # TODO: add error handling
        session_id = int(session_id)
        previous_state: TicTacToeModel.TicTacToeDTO = GlobalSessionState.get_session(session_id)
        delta = TicTacToeDelta.from_dict(request.get_json(force=True))
        next_state: TicTacToeModel.TicTacToeDTO = TicTacToeDelta.apply_delta(to=previous_state, delta=delta)
        GlobalSessionState.update_session(session_id, next_state)
        return next_state.json(), 200
