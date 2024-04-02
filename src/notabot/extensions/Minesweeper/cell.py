class Cell:
    mine_emoji = ":boom:"
    count_emojis = [
        ":zero:",
        ":one:",
        ":two:",
        ":three:",
        ":four:",
        ":five:",
        ":six:",
        ":seven:",
        ":eight:",
        ":nine:"
    ]

    def __init__(self) -> None:
        self.is_mine = False
        self.mines_around = 0

    def __str__(self) -> str:
        if self.is_mine:
            return Cell.mine_emoji
        return Cell.count_emojis[self.mines_around]

    def __repr__(self) -> str:
        return f"Cell(\"{self.__str__()}\")"
