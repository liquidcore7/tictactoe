from typing import *

from models.state import TicTacToeModel, TicTacToeDelta, TicTacToeHelper
from persistance.inject import WithDataBase


class SessionService(WithDataBase[TicTacToeModel.TicTacToeDTO]):
    def __init__(self):
        super().__init__(lambda dto: dto.json(), lambda string: TicTacToeModel.from_json(string))

    def create_session(self) -> Optional[str]:
        success, session_id = self.db.create(TicTacToeModel.empty())
        if not success:
            return None
        return session_id

    def get_session(self, session_id: str) -> Optional[TicTacToeModel.TicTacToeDTO]:
        return self.db.get(session_id)

    def update_session(self, session_id: str, with_value: TicTacToeDelta.TicTacToeDeltaDTO) \
            -> Optional[TicTacToeModel.TicTacToeDTO]:

        maybe_previous_state: Optional[TicTacToeModel.TicTacToeDTO] = self.get_session(session_id)
        if maybe_previous_state is None:
            return None

        # TODO: validate delta
        next_state: TicTacToeModel.TicTacToeDTO = TicTacToeDelta.apply_delta(maybe_previous_state, with_value)
        updated_successfully, instance = self.db.update(session_id, next_state,
                                                        last_update=next_state.winner != TicTacToeHelper.Players.FREE)
        return instance if updated_successfully else None

    def delete_session(self, session_id: str) -> bool:
        return self.db.delete(session_id)
