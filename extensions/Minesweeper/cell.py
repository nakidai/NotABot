class Cell:
    def __init__(self) -> None:
        self.is_mine = False
        self.mines_around = 0

    def __str__(self) -> str:
        if self.is_mine:
            return "BM"
        if self.mines_around == 0:
            return "  "
        return f"{self.mines_around:2}"

    def __repr__(self) -> str:
        return f"Cell(\"{self.__str__()}\")"
