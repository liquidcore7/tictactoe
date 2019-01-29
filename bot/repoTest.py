import unittest
from bot.repository import BotRepository
from persistance.inject import WithDataBase


class BotRepositoryTest(unittest.TestCase):

    def test_construct_properly(self):
        WithDataBase().db.delete(BotRepository.BOT_UUID)  # make sure no cached copy available
        repo: BotRepository = BotRepository()
        self.assertTrue(True, 'should construct first time')

    def test_construct_after_cached(self):
        repo: BotRepository = BotRepository()
        self.assertTrue(True, 'should construct when cached')
