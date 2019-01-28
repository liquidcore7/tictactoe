from bot.tree import TicTacToeDecisionTree
from persistance.inject import WithDataBase
from typing import *
import pickle


class BotModel(WithDataBase[TicTacToeDecisionTree]):
    BOT_UUID = 'bot_instance'

    def __init__(self):
        super().__init__(lambda obj: pickle.dumps(obj), lambda json: pickle.loads(json))
        maybe_bot: Optional[TicTacToeDecisionTree] = self.db.get(BotModel.BOT_UUID)
        if maybe_bot is None:
            maybe_bot: TicTacToeDecisionTree = TicTacToeDecisionTree()  # time consuming, will train. TODO: async
            self.db.create(maybe_bot, with_name=BotModel.BOT_UUID)
        self.bot = maybe_bot
