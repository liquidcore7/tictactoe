import json
import unittest
from models.state import *


class TicTacToeModelTest(unittest.TestCase):

    def test_empty_field(self):
        empty_field = TicTacToeModel.empty()
        self.assertEqual(
            empty_field.winner,
            TicTacToeHelper.Players.FREE,
            'Empty field should not be won'
        )

    def test_won_by_X(self):
        x, o = int('111000000', 2), int('000110000', 2)
        x_field = TicTacToeModel.of(xs=x, os=o)
        self.assertEqual(
            x_field.winner,
            TicTacToeHelper.Players.X,
            'First row filled with X should be won by X'
        )

    def test_won_by_O(self):
        x, o = int('110100000', 2), int('001010100', 2)
        o_field = TicTacToeModel.of(xs=x, os=o)
        self.assertEqual(
            o_field.winner,
            TicTacToeHelper.Players.O,
            'Right to left diagonal filled with O should be won by O'
        )

    def test_json_deserialization(self):
        empty_field = TicTacToeModel.empty()
        self.assertEqual(
            empty_field.json(),
            json.dumps({'xs': 0, 'os': 0, 'winner': '-'}),
            'Generated json should be correct'
        )

    def test_json_serialization(self):
        empty_json = json.dumps({'xs': 0, 'os': 0, 'winner': '-'})
        self.assertEqual(
            TicTacToeModel.from_json(empty_json),
            TicTacToeModel.empty(),
            'Should construct from json'
        )


class TicTacToeDeltaTest(unittest.TestCase):

    def test_static_constructor(self):
        delta = TicTacToeDelta.of('X', 0)
        self.assertEqual(
            delta.player,
            TicTacToeHelper.Players.X,
            'Should properly convert player'
        )
        self.assertEqual(
            delta.updated_field,
            0,
            'Should properly assign updated value'
        )

    def test_apply_delta(self):
        not_won = TicTacToeModel.of(int('110000000', 2), int('000110000', 2))
        winning_delta = TicTacToeDelta.of('X', int('001000000', 2))
        won_field = TicTacToeDelta.apply_delta(not_won, winning_delta)
        self.assertEqual(
            won_field.xs,
            int('111000000', 2),
            'Delta should be properly applied'
        )
        self.assertEqual(
            won_field.winner,
            TicTacToeHelper.Players.X,
            'Winner should be properly calculated after delta applied'
        )

    def test_serialize_json(self):
        empty_delta_json = json.dumps({'player': '-', 'updated_field': 0})
        delta = TicTacToeDelta.from_json(empty_delta_json)
        self.assertEqual(
            TicTacToeDelta.apply_delta(TicTacToeModel.empty(), delta),
            TicTacToeModel.empty(),
            'Should be properly constructed from json'
        )

    def test_from_dict(self):
        empty_delta_json = {'player': '-', 'updated_field': 0}
        delta = TicTacToeDelta.from_dict(empty_delta_json)
        self.assertEqual(
            TicTacToeDelta.apply_delta(TicTacToeModel.empty(), delta),
            TicTacToeModel.empty(),
            'Should be properly constructed from dict'
        )
