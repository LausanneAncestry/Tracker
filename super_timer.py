from time import time
from typing import Optional


class Timer:
    def __init__(self, start_message: Optional[str] = None):
        if start_message:
            print(start_message)
        self.start_at = time()

    def tac(self, sentence="Elapsed time: {TIME}"):
        print(sentence.replace("{TIME}", f"{round(time() - self.start_at, 4)}s"))
