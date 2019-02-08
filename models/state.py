from enum import Enum
from typing import *
from pydantic import BaseModel


class TicTacToeHelper:

    WON_MASKS: List[int] = list(map(lambda mask: int(mask, 2), [
        '111000000',  # row 1
        '000111000',  # row 2
        '000000111',  # row 3
        '100010001',  # diagonal: left to right
        '001010100',  # diagonal: right to left
        '100100100',  # col 1
        '010010010',  # col 2
        '001001001'  # col 3
    ]))

    class Players(Enum):
        X = 'X'
        O = 'O'
        FREE = '-'

    @staticmethod
    def won_by(xs: int, os: int) -> Players:
        for mask in TicTacToeHelper.WON_MASKS:
            if xs & mask == mask:
                return TicTacToeHelper.Players.X
            if os & mask == mask:
                return TicTacToeHelper.Players.O
        return TicTacToeHelper.Players.FREE


class TicTacToeModel:

    class TicTacToeDTO(BaseModel):
        xs: int
        os: int
        winner: TicTacToeHelper.Players

    @staticmethod
    def from_json(json: str) -> TicTacToeDTO:
        return TicTacToeModel.TicTacToeDTO.parse_raw(json)

    @staticmethod
    def is_won(field: TicTacToeDTO) -> bool:
        return TicTacToeHelper.won_by(field.xs, field.os) != TicTacToeHelper.Players.FREE \
                or field.xs | field.os == 511  # all cells filled

    @staticmethod
    def of(xs: int, os: int) -> TicTacToeDTO:
        return TicTacToeModel.TicTacToeDTO(xs=xs, os=os, winner=TicTacToeHelper.won_by(xs, os))

    @staticmethod
    def empty() -> TicTacToeDTO:
        return TicTacToeModel.TicTacToeDTO(xs=0, os=0, winner=TicTacToeHelper.Players.FREE)


class TicTacToeDelta:

    class TicTacToeDeltaDTO(BaseModel):
        player: TicTacToeHelper.Players
        updated_field: int

    @staticmethod
    def of(player: str, updated_field: int) -> TicTacToeDeltaDTO:
        return TicTacToeDelta.TicTacToeDeltaDTO(player=TicTacToeHelper.Players(player),
                                                updated_field=updated_field)

    @staticmethod
    def empty() -> TicTacToeDeltaDTO:
        return TicTacToeDelta.of(TicTacToeHelper.Players.FREE.value, 0)

    @staticmethod
    def from_json(json: str) -> TicTacToeDeltaDTO:
        return TicTacToeDelta.TicTacToeDeltaDTO.parse_raw(json)

    @staticmethod
    def from_dict(data: Dict[str, Union[int, str]]) -> TicTacToeDeltaDTO:
        return TicTacToeDelta.TicTacToeDeltaDTO.parse_obj(data)

    @staticmethod
    def apply_delta(to: TicTacToeModel.TicTacToeDTO, delta: TicTacToeDeltaDTO) -> TicTacToeModel.TicTacToeDTO:
        if delta.player == TicTacToeHelper.Players.X:
            return TicTacToeModel.of(to.xs | delta.updated_field, to.os)
        elif delta.player == TicTacToeHelper.Players.O:
            return TicTacToeModel.of(to.xs, to.os | delta.updated_field)
        else:
            return to
