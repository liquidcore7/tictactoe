import pickle
from typing import *
from functools import reduce
from copy import copy

from bot.repository import BotRepository
from bot.tree import TicTacToeDecisionTree
from models.state import TicTacToeDelta, TicTacToeModel, TicTacToeHelper
from persistance.inject import WithDataBase
from services.session import SessionService

from singleton_decorator import singleton


@singleton
class BotService(WithDataBase[List[TicTacToeDelta.TicTacToeDeltaDTO]]):

    def __init__(self):
        super().__init__(lambda dto_list: pickle.dumps(list(map(lambda dto: dto.json(), dto_list))),
                         lambda string: list(map(TicTacToeDelta.from_json, pickle.loads(string))))
        self.BOT_POSTFIX = '_moves'
        self.session_service = SessionService()
        self.bot_root_node = BotRepository().get_root()

    def __append__(self, session_id: str, value: TicTacToeDelta.TicTacToeDeltaDTO) -> bool:
        current_moves = self.get_session(session_id)
        current_moves.append(value)
        return self.db.update(session_id + self.BOT_POSTFIX, current_moves)[0]

    def __next_move__(self, previous_moves: List[TicTacToeDelta.TicTacToeDeltaDTO]) \
            -> Optional[TicTacToeDelta.TicTacToeDeltaDTO]:

        root = copy(self.bot_root_node)
        last_move = reduce(lambda leaf, move: copy(leaf.find(move)), previous_moves, root)

        maybe_next = TicTacToeDecisionTree.next(last_move)
        return maybe_next.value if maybe_next else None

    def create_session(self) -> Optional[str]:
        maybe_session_id: Optional[str] = self.session_service.create_session()
        if maybe_session_id is None:
            return None

        status_success, _ = self.db.create(list(), with_name=maybe_session_id + self.BOT_POSTFIX)
        return maybe_session_id if status_success else None

    def get_session(self, session_id: str) -> List[TicTacToeDelta.TicTacToeDeltaDTO]:
        return self.db.get(session_id + self.BOT_POSTFIX)

    def update_session(self, session_id: str, with_value: TicTacToeDelta.TicTacToeDeltaDTO) \
            -> Optional[TicTacToeModel.TicTacToeDTO]:
        # do player's turn if it's player isn't Players.FREE
        if with_value.player != TicTacToeHelper.Players.FREE:
            maybe_player_field = self.session_service.update_session(session_id, with_value)
            # update moves for bot
            self.__append__(session_id, with_value)

        # get potential next move if any
        all_moves: List[TicTacToeDelta.TicTacToeDeltaDTO] = self.db.get(session_id + self.BOT_POSTFIX)
        maybe_next_move: Optional[TicTacToeDelta.TicTacToeDeltaDTO] = self.__next_move__(all_moves)

        if maybe_next_move is None:  # if end of game reached, return without bot's move
            self.delete_session(session_id)
            return maybe_player_field

        self.__append__(session_id, maybe_next_move)
        maybe_resulting_field = self.session_service.update_session(session_id, maybe_next_move)

        if maybe_resulting_field.winner != TicTacToeHelper.Players.FREE:
            self.delete_session(session_id)
        return maybe_resulting_field

    def delete_session(self, session_id: str) -> bool:
        status = self.session_service.delete_session(session_id)
        return status and self.db.delete(session_id + self.BOT_POSTFIX)
