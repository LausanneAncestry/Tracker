from Levenshtein import ratio
from typing import Optional

from time import time

def safe_cast_to_int(s: str) -> Optional[int]:
	try:
		return int(s)
	except ValueError:
		return None
	except TypeError:
		return None

def in_range_or_None(test_value: any, left: any, right: any):
	test_value = safe_cast_to_int(test_value)
	if isinstance(test_value, int) and (left <= test_value <= right):
		return test_value
	return None

def value_or_None(test_str: str):
	if not isinstance(test_str, str):
		return None
	if test_str in [None, "", ".", "·", "?"]:
		return None
	return test_str

# close enough is good enough
def are_close_enough(name1: str, name2: str, cutoff: float = 0.8) -> bool:
	if not isinstance(name1, str) or not isinstance(name2, str):
		return False
	# see documentation here: https://rapidfuzz.github.io/Levenshtein/levenshtein.html
	return True if ratio(name1.lower(), name2.lower(), score_cutoff=cutoff) > 0.0 else False

class Timer:
    def __init__(self, start_message: Optional[str] = None):
        if start_message:
            print(start_message)
        self.start_at = time()

    def tac(self, sentence="Done in {TIME}"):
        print(sentence.replace("{TIME}", f"{round(time() - self.start_at, 4)}s"))