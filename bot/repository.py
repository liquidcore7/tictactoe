from bot.tree import TicTacToeDecisionTree, Leaf, TicTacToeDecisionTreeScore
from models.state import TicTacToeDelta
from persistance.inject import WithDataBase

from singleton_decorator import singleton

from typing import *
import pickle

TreeNode = Leaf[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore]


@singleton
class BotRepository(WithDataBase[TreeNode]):

    def __init__(self):
        self.BOT_UUID = 'bot_instance'
        super().__init__(serializer=pickle.dumps, deserializer=pickle.loads)

        maybe_bot: Optional[TreeNode] = self.db.get(self.BOT_UUID)
        if maybe_bot is None:
            maybe_bot: TreeNode = TicTacToeDecisionTree().get_root()
            self.db.create(maybe_bot, with_name=self.BOT_UUID, expires=False)
        self.decisions_root: TreeNode = maybe_bot

    def get_root(self):
        return self.decisions_root
