from typing import List, Tuple

DICTIONARY_FILE = "all_jobs.csv"

def match_jobs_with_dictionary(jobs_to_match: List[Tuple[int, str]]) -> List[Tuple[int, int]]:
	"""
	Matches raw job names to job IDs using a predefined dictionary.

	This function takes a list of tuples, where each tuple contains a person ID and a raw job name.
	It returns a list of tuples with the person ID and the corresponding job ID. If no job is found
	in the dictionary, the job ID is set to 0.

	Parameters:
	jobs_to_match (List[Tuple[int, str]]): A list of tuples where each tuple contains a person ID and a raw job name.

	Returns:
	List[Tuple[int, int]]: A list of tuples where each tuple contains a person ID and the corresponding job ID.
	"""
	return []