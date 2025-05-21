import pandas as pd
import unicodedata
from rapidfuzz import fuzz
from typing import List, Tuple

DICTIONARY_FILE = "all_jobs_1.csv"
METADATA_FILE = "jobs_metadata.csv"
THRESHOLD = 90

alljobs = pd.read_csv(DICTIONARY_FILE)
jobs_metadata = pd.read_csv(METADATA_FILE)

def normalize_string(s):
	if not isinstance(s, str):
		return ''
	# Remove spaces and special characters
	s = ''.join(c for c in s if c.isalnum())
	# Normalize accented characters to their base form
	s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
	return s.lower()

# Function for fuzzy matching
def fuzzy_match(term, choices, threshold=THRESHOLD):
	best_match = None
	best_score = 0
	for choice in choices:
		score = fuzz.ratio(term, choice)
		if score > best_score:
			best_score = score
			best_match = choice
	if best_score >= threshold:
		return best_match, best_score
	return None, 0


# Normalize the 'titre' column in the 'all' table
alljobs['normalized_titre'] = alljobs['titre'].apply(normalize_string)

# Expand synonyms in 'all' dataframe
expanded_rows = []
for index, row in alljobs.iterrows():
	synonyms = row['titre'].split('|')  # Split multiple synonyms
	for synonym in synonyms:
		expanded_rows.append(
			{'index': index, 'titre': synonym.strip(), 'normalized_titre': normalize_string(synonym.strip())})

# Convert expanded rows into DataFrame
all_expanded = pd.DataFrame(expanded_rows)

def match_job_with_dictionary(raw_job: str) -> Tuple[int, str]:
	if not raw_job or not isinstance(raw_job, str):
		return 10019, "sans emploi"
	
	normalized_term = normalize_string(raw_job.strip())
	match = all_expanded.loc[all_expanded['normalized_titre'] == normalized_term]
	if match.empty:
		# Try fuzzy match
		best_match, _ = fuzzy_match(normalized_term, all_expanded['normalized_titre'])
		if best_match:
			match = all_expanded.loc[all_expanded['normalized_titre'] == best_match]

	job_id = match["index"].values[0] if not match.empty else -1
	job_name = match["titre"].values[0] if not match.empty else "emploi inconnu"

	return int(job_id), job_name


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
	matched = []

	for person_id, raw_job in jobs_to_match:
		if not raw_job or not isinstance(raw_job, str):
			matched.append((person_id, -1))
			continue
		normalized_term = normalize_string(raw_job.strip())
		match = all_expanded[all_expanded['normalized_titre'] == normalized_term]
		job_id = match.iloc[0]['index'] if not match.empty else -1
		if match.empty:
			# Try fuzzy match
			best_match, best_score = fuzzy_match(normalized_term, all_expanded['normalized_titre'])
			if best_match:
				match = all_expanded[all_expanded['normalized_titre'] == best_match]
				job_id=str(match.index[0])# Use the index as the ID
		matched.append((person_id, job_id))

	return matched


def get_job_metadata(job_name):
	# Find the row corresponding to the job_name
	job_row = jobs_metadata[jobs_metadata['job'] == job_name]

	# Check if the job was found
	if not job_row.empty:
		# Convert the row to a dictionary
		job_metadata = job_row.iloc[0].to_dict()
		job_metadata = {k: (None if pd.isna(v) else v) for k, v in job_metadata.items()}
		return job_metadata
	else:
		return None