from db import Person, personToInfo, PersonInfo, CensusEntryInfo, get_all_person_entries, get_census_entries_of_person
import json
import os
import sys
from job_matcher import match_job_with_dictionary, get_job_metadata

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Set
from utils import Timer


@dataclass
class PersonWithCensusEntries(PersonInfo):
	census_entries: Dict[str, CensusEntryInfo] = field(default_factory=dict)

def find_persons_to_export() -> List[PersonWithCensusEntries]:
	people_to_export: List[PersonWithCensusEntries] = []
	all_people = get_all_person_entries()
	people_with_fathers = [person for person in all_people if person.parent != None]
	for person in people_with_fathers:
		if person.parent != None:
			parent: Person = Person.get(Person.id == person.parent)
			if parent.parent == None:
				parent = personToInfo(parent)
				parent: PersonWithCensusEntries = PersonWithCensusEntries(**asdict(parent))
				parent.census_entries = get_census_entries_of_person(parent.id)
				people_to_export.append(parent)

		person = PersonWithCensusEntries(**asdict(person))
		person.census_entries = get_census_entries_of_person(person.id)
		people_to_export.append(person)
	return people_to_export

def export_job_set(job_set: Set[Tuple[int, str]]):
	job_list = sorted(list(job_set), key=lambda x: x[1])
	jobs_metadata = {}
	missing = 0
	for job_id, job_name in job_list:
		metadata = get_job_metadata(job_name)
		if metadata:
			jobs_metadata[job_id] = metadata
		else:
			missing += 1
			jobs_metadata[job_id] = {
				"job": f"{job_name} (no metadata)"
			}
			print(f"Missing metadata for {job_id}:{job_name}")

	print(f"Number of unique jobs: {len(job_set)}")
	print(f"Found metadata for: {len(jobs_metadata.keys())} jobs")
	print(f"Missing metadata for: {missing} jobs")
	return jobs_metadata
	

def json_export(target="./out/tracked.json", indent=None, job_ids=True):
	"""
	Exports a list of people with their census entries to a JSON file.

	This function retrieves all person entries from the database, filters those
	who have a parent, and processes each person to include their census entries.
	If a person's parent does not have a parent themselves, the parent's information
	is also included in the export. The resulting data is written to 'export.json'
	in the 'out' directory.

	Steps:
	1. Retrieve all person entries from the database.
	2. Filter persons who have a parent.
	3. For each person with a parent, retrieve and include the parent's information
	   if the parent does not have a parent themselves.
	4. Convert each person to a PersonWithCensusEntries object and retrieve their
	   census entries.
	5. If job_ids is true, it tries to match jobs to the ids contained in job_dictionary.csv 
	6. Ensure the 'out' directory exists and write the data to 'export.json'.
	"""

	timer = Timer(f"Exporting to {target}...")
	people_to_export = find_persons_to_export()

	data = {
		"persons": list(map(asdict, people_to_export)),
	}

	if job_ids:
		people_with_job_ids = []
		job_set = set()
		for person in people_to_export:
			person_with_job_ids = asdict(person)
			person_with_job_ids["job_ids"] = []
			for entry in person.census_entries:
				job_id, job_name = match_job_with_dictionary(entry.job)
				person_with_job_ids["job_ids"].append(job_id)
				job_set.add((job_id, job_name))
			people_with_job_ids.append(person_with_job_ids)
	
		data = {
			"persons": people_with_job_ids,
			"jobs": export_job_set(job_set)
		}
	else:
		data = {
			"persons": list(map(asdict, people_to_export)),
		}

	os.makedirs(os.path.dirname(target), exist_ok=True)
	with open(target, 'w', encoding='utf-8') as json_file:
		json.dump(data, json_file, indent=indent, ensure_ascii=False)
		timer.tac()

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		json_export(sys.argv[1])
	else:
		json_export()

