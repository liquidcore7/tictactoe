from __future__ import annotations
from typing import *
from copy import copy
from models.state import *

T = TypeVar('T')
SC = TypeVar('SC')


class Leaf(Generic[T, SC]):
    def __init__(self, value: T, score: SC, depth: int=0):
        self.value: T = value
        self.depth: int = depth
        self.score: SC = score
        self.children: Set[Leaf[T, SC]] = set()

    def append(self, node: T, score: SC):
        self.children.add(Leaf(node, score, self.depth + 1))

    # key func is a mapping from SC type to comparable type (with __lt__ defined)
    def next(self, key_func=lambda x: x) -> Optional[Leaf[T, SC]]:
        if len(self.children) > 0:
            return max(self.children, key=lambda leaf: key_func(leaf.score))
        return None

    def find(self, child: T) -> Optional[Leaf[T, SC]]:
        for c in self.children:
            if c.value == child:
                return c
        return None


class Tree(Generic[T, SC]):
    def __init__(self, initial_value: T, initial_score: SC):
        self.root: Leaf[T, SC] = Leaf(initial_value, initial_score, 0)

    def get_root(self) -> Leaf[T, SC]:
        return copy(self.root)


class TicTacToeDecisionTreeScore:
    SCORE = 10

    def __init__(self, score: int):
        self.value = score

    @staticmethod
    def from_winner(winner: TicTacToeHelper.Players, tree_depth: int) -> TicTacToeDecisionTreeScore:
        if winner == TicTacToeHelper.Players.FREE:
            return TicTacToeDecisionTreeScore.empty()

        score = TicTacToeDecisionTreeScore.SCORE - (tree_depth - 5) if winner == TicTacToeHelper.Players.X else \
            -TicTacToeDecisionTreeScore.SCORE + (tree_depth - 6)

        return TicTacToeDecisionTreeScore(score)

    @staticmethod
    def empty():
        return TicTacToeDecisionTreeScore(0)


class TicTacToeDecisionTree(Tree[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore]):

    all_moves = [(1 << power) for power in range(9)]
    best_picker = lambda player: lambda score: -score.value if player == TicTacToeHelper.Players.X else score.value

    @staticmethod
    def get_moves(field_state: TicTacToeModel.TicTacToeDTO, player: TicTacToeHelper.Players) \
            -> List[TicTacToeDelta.TicTacToeDeltaDTO]:

        if field_state.winner != TicTacToeHelper.Players.FREE:
            return []

        def filter_available(state: int) -> List[TicTacToeDelta.TicTacToeDeltaDTO]:
            return list(map(lambda move: TicTacToeDelta.of(player.value, move),
                            filter(lambda move: (move & state) == 0, TicTacToeDecisionTree.all_moves))
                        )

        return filter_available(field_state.xs | field_state.os)

    # Should return X if current player is Players.Free (for the first turn)
    @staticmethod
    def negate_player(player: TicTacToeHelper.Players) -> TicTacToeHelper.Players:
        return TicTacToeHelper.Players.O if player == TicTacToeHelper.Players.X else TicTacToeHelper.Players.X

    @staticmethod
    def get_score(field_state: TicTacToeModel.TicTacToeDTO, depth: int) -> TicTacToeDecisionTreeScore:
        return TicTacToeDecisionTreeScore.from_winner(field_state.winner, depth)

    def train(self):

        def recursive_set_weights(transformation: Leaf[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore],
                                  parent_model: TicTacToeModel.TicTacToeDTO,
                                  current_player: TicTacToeHelper.Players):

            current_model: TicTacToeModel.TicTacToeDTO = TicTacToeDelta.apply_delta(parent_model, transformation.value)
            next_player = TicTacToeDecisionTree.negate_player(current_player)
            next_level: List[TicTacToeDelta.TicTacToeDeltaDTO] = TicTacToeDecisionTree.get_moves(current_model, next_player)

            if len(next_level) == 0:
                transformation.score = TicTacToeDecisionTree.get_score(current_model, transformation.depth)
                return
            else:
                for n in next_level:
                    transformation.append(n, TicTacToeDecisionTreeScore.empty())

            for move_leaf in transformation.children:
                recursive_set_weights(move_leaf, current_model, next_player)

            maybe_max = max(map(lambda leaf: leaf.score.value, transformation.children))
            maybe_min = min(map(lambda leaf: leaf.score.value, transformation.children))
            new_value = maybe_max if abs(maybe_max) >= abs(maybe_min) else maybe_min
            transformation.score = TicTacToeDecisionTreeScore(new_value)
            return

        recursive_set_weights(self.root, TicTacToeModel.empty(), TicTacToeHelper.Players.FREE)

    def __init__(self):
        super().__init__(TicTacToeDelta.of(TicTacToeHelper.Players.FREE.value, updated_field=0),
                         TicTacToeDecisionTreeScore.empty())
        self.train()

    @staticmethod
    def next(leaf: Leaf[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore]) \
        -> Leaf[TicTacToeDelta.TicTacToeDeltaDTO, TicTacToeDecisionTreeScore]:

        return leaf.next(TicTacToeDecisionTree.best_picker(leaf.value.player))
