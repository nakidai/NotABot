from typing import Callable
from os.path import abspath, join

def set_root(root: str) -> Callable[[str], str]:
    return lambda path: join(abspath(root), path)
