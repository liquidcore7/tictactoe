from bot.tree import TicTacToeDecisionTree, Leaf, TicTacToeDecisionTreeScore
from models.state import TicTacToeDelta
from persistance.inject import WithDataBase
from typing import *
import pickle
from copy import deepcopy

TreeNode = Leaf[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore]


class BotRepository(WithDataBase[TreeNode]):
    BOT_UUID = 'bot_instance'

    def __init__(self):
        super().__init__(serializer=pickle.dumps, deserializer=pickle.loads)

        maybe_bot: Optional[TreeNode] = self.db.get(BotRepository.BOT_UUID)
        if maybe_bot is None:
            maybe_bot: TreeNode = TicTacToeDecisionTree().get_root()
            self.db.create(maybe_bot, with_name=BotRepository.BOT_UUID, expires=False)
        self.decisions_root: TreeNode = maybe_bot

    def get_root(self):
        return deepcopy(self.decisions_root)
