import os
from pathlib import Path
from typing import List

class Filestore:

    def __init__(self, path_dir: str) -> None:
        self.path_dir = path_dir

    def get_path_file(self, key) -> str:
        return os.path.join(self.path_dir, key)

    def exists(self, key) -> bool:
        return self.path.is_file(self.get_path_file(key))
