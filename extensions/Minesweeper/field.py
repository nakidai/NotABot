from typing import List
from random import randint

from extensions.Minesweeper import cell


class Field:
    def __init__(
        self,

        field_size: int,
        mines_amount: int
    ) -> None:
        self.field_size: int = field_size
        self.mines_amount: int = mines_amount
        self.field: List[List[cell.Cell]] = [[]]

    def generate(self) -> None:
        self.field = \
            [
                [None] * self.field_size for _ in range(self.field_size)
            ]
        for i in range(self.field_size):
            for j in range(self.field_size):
                self.field[j][i] = cell.Cell()
        mines_left = self.mines_amount
        while mines_left:
            x = randint(0, self.field_size - 1)
            y = randint(0, self.field_size - 1)
            if self.field[y][x].is_mine:
                continue
            self.field[y][x].is_mine = True
            for i in range(-1, 2):
                for j in range(-1, 2):
                    rx = x + i
                    ry = y + j
                    if rx < 0 or ry < 0 or \
                       rx >= self.field_size or ry >= self.field_size:
                        continue
                    self.field[ry][rx].mines_around += 1
            mines_left -= 1

    def __str__(self) -> str:
        out = ""
        for line in self.field:
            for field_cell in line:
                out += f"||{field_cell}||"
            out += '\n'
        return out[:-1]
