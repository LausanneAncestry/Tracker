from db import PersonInfo
from Levenshtein import ratio
import pandas as pd
from utils import normalize_string

from typing import List, Tuple, Dict

THRESHOLD = 0.8

def fuzzy_match(term: str, jobs: List[Tuple[int, str]], threshold=THRESHOLD):
	term = normalize_string(term)
	best_match = None
	best_score = 0
	for choice in jobs:
		for job in choice[1].split(","): # handle synonyms
			score = ratio(term, normalize_string(job), score_cutoff=threshold)
			if score > best_score:
				best_score = score
				best_match = choice
	if best_score >= threshold:
		return best_match[0]
	return None

def match_jobs_to_ids(persons: List[Dict]):
	job_list = pd.read_csv("job_dictionary.csv", delimiter=";")
	job_list = list(job_list.itertuples(index=False, name=None))
	for person in persons:
		person["job"] = []
		for entry in person["census_entries"]:
			person["job"].append(fuzzy_match(entry["job"], job_list))