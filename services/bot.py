import json
from typing import *
from functools import reduce

from bot.repository import BotRepository
from bot.tree import TicTacToeDecisionTree
from models.state import TicTacToeDelta, TicTacToeModel, TicTacToeHelper
from persistance.inject import WithDataBase
from services.session import SessionService


class BotService(WithDataBase[List[TicTacToeDelta.TicTacToeDeltaDTO]]):
    BOT_POSTFIX = '_moves'

    def __init__(self):
        super().__init__(lambda dto_list: json.dumps(list(map(lambda dto: dto.json(), dto_list))),
                         lambda string: list(map(TicTacToeDelta.from_json, json.loads(string))))
        self.session_service = SessionService()
        self.bot_root_node = BotRepository().get_root()

    def __append__(self, session_id: str, value: TicTacToeDelta.TicTacToeDeltaDTO) -> bool:
        return self.db.db_connection.rpushx(session_id + BotService.BOT_POSTFIX, self.db.serde[0](value))

    def __next_move__(self, previous_moves: List[TicTacToeDelta.TicTacToeDeltaDTO]) \
            -> Optional[TicTacToeDelta.TicTacToeDeltaDTO]:

        root = self.bot_root_node
        last_move = reduce(lambda leaf, move: leaf.find(move), previous_moves, root)

        maybe_next = TicTacToeDecisionTree.next(last_move)
        return maybe_next.value if maybe_next else None

    def create_session(self) -> Optional[str]:
        maybe_session_id: Optional[str] = self.session_service.create_session()
        if maybe_session_id is None:
            return None

        status_success, _ = self.db.create(list(), with_name=maybe_session_id + BotService.BOT_POSTFIX)
        return maybe_session_id if status_success else None

    def get_session(self, session_id: str) -> Optional[TicTacToeDelta.TicTacToeDeltaDTO]:
        return self.session_service.get_session(session_id)

    def update_session(self, session_id: str, with_value: TicTacToeDelta.TicTacToeDeltaDTO) \
            -> Optional[TicTacToeModel.TicTacToeDTO]:

        player_inserted, player_field = self.session_service.update_session(session_id, with_value)

        self.__append__(session_id, with_value)
        all_moves: List[TicTacToeDelta.TicTacToeDeltaDTO] = self.db.get(session_id + BotService.BOT_POSTFIX)
        maybe_next_move: Optional[TicTacToeDelta.TicTacToeDeltaDTO] = self.__next_move__(all_moves)
        if maybe_next_move is None:
            if player_field.winner != TicTacToeHelper.Players.FREE:
                self.delete_session(session_id)

            return player_field if player_inserted else None

        self.__append__(session_id, maybe_next_move)
        bot_inserted, resulting_field = self.session_service.update_session(session_id, maybe_next_move)
        if resulting_field.winner != TicTacToeHelper.Players.FREE:
            self.delete_session(session_id)

        return resulting_field if bot_inserted else None

    def delete_session(self, session_id: str) -> bool:
        return self.db.delete(session_id + BotService.BOT_POSTFIX)
