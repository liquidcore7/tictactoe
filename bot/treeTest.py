import unittest
from bot.tree import *


class LeafTest(unittest.TestCase):

    def test_creating_leaf(self):
        leaf: Leaf[int] = Leaf(value=10, score=2.0)
        self.assertEqual(
            leaf.children,
            set(),
            'Leaf shouldn`t have children'
        )
        self.assertEqual(
            leaf.depth,
            0,
            'Depth should be zero by default'
        )
        self.assertEqual(
            leaf.value,
            10.0,
            'Leaf value should be as constructed'
        )

    def test_appending_leaf(self):
        root: Leaf[int] = Leaf(value=0, score=0.0)
        for i in range(3):
            root.append(i, float(i))

        self.assertEqual(
            len(root.children),
            3,
            'Root should have all children attached'
        )

        self.assertEqual(
            root.children.pop().value in range(3),
            True,
            'Children values should be correct'
        )

        self.assertEqual(
            root.children.pop().depth,
            1,
            'Children of root node should have depth = 1'
        )

    def test_best_child(self):
        root: Leaf[int] = Leaf(0, 0.0)
        children = [i for i in range(3)]
        for c in children:
            root.append(c, float(c))

        obtained_children = []
        best = root.next()
        while best.score != -1000:
            obtained_children.append(best.value)
            best.score = -1000
            best = root.next()

        obtained_children.reverse()

        self.assertEqual(
            children,
            obtained_children,
            'Pick best child should work properly'
        )

    def test_find_next(self):
        root: Leaf[int] = Leaf(0, 0.0)
        root.append(1, 1.0)
        self.assertEqual(
            root.find(1).score,
            1.0,
            'Children search should work properly'
        )


class TreeTest(unittest.TestCase):
    def test_init(self):
        tree: Tree[int] = Tree(1)
        self.assertEqual(
            tree.root.value,
            1,
            'Should properly initialize tree'
        )

    def test_copy_root(self):
        tree: Tree[int] = Tree(1)
        root = tree.root
        copy_root = tree.get_root()
        self.assertFalse(
            root is copy_root,
            'References to root shouldn`t be same'
        )
        copy_root = None
        self.assertTrue(
            root is not None,
            'Rebinding copy reference shouldn`t affect tree'
        )


class TicTacToeDecisionTreeTest(unittest.TestCase):
    def test_negate_player(self):
        first_player = TicTacToeHelper.Players.FREE
        self.assertEqual(
            TicTacToeDecisionTree.negate_player(first_player),
            TicTacToeHelper.Players.X,
            'FREE negate should be X'
        )
        X_player = TicTacToeHelper.Players.X
        self.assertEqual(
            TicTacToeDecisionTree.negate_player(X_player),
            TicTacToeHelper.Players.O,
            'X negate should be O'
        )
        O_player = TicTacToeHelper.Players.O
        self.assertEqual(
            TicTacToeDecisionTree.negate_player(O_player),
            TicTacToeHelper.Players.X,
            'O negate should be X'
        )

    def test_available_moves(self):
        empty_field = TicTacToeModel.empty()
        self.assertEqual(
            len(TicTacToeDecisionTree.get_moves(empty_field, TicTacToeHelper.Players.X)),
            9,
            'There are 9 available first moves'
        )
        won = TicTacToeModel.of(xs=7, os=24)
        self.assertEqual(
            len(TicTacToeDecisionTree.get_moves(won, TicTacToeHelper.Players.O)),
            0,
            'No moves on a won field'
        )
        one_possible = TicTacToeModel.of(xs=int('110001100', 2), os=int('001110010', 2))
        self.assertEqual(
            len(TicTacToeDecisionTree.get_moves(one_possible, TicTacToeHelper.Players.O)),
            1,
            'No moves on a tie field'
        )
        self.assertEqual(
            len(TicTacToeDecisionTree.get_moves(one_possible, TicTacToeHelper.Players.X)),
            1,
            'One move for one empty cell'
        )

    def test_train(self):
        trained = TicTacToeDecisionTree()
        player = TicTacToeHelper.Players.X
        field = TicTacToeModel.empty()
        best = lambda player: lambda score: score.max if player == TicTacToeHelper.Players.X else -score.max
        best_move = trained.get_root().next(best(player))
        while best_move is not None:
            field = TicTacToeDelta.apply_delta(field, best_move.value)
            print(field)
            print(best_move.score.max, best_move.score.min)
            player = TicTacToeDecisionTree.negate_player(player)
            best_move = best_move.next(best(player))


        self.assertEqual(
            field.winner,
            TicTacToeHelper.Players.FREE,
            'Best moves should cause a tie'
        )
