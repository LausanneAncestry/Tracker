from db import Person, personToInfo, PersonInfo, CensusEntryInfo, get_all_person_entries, get_census_entries_of_person
import json
import os

from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass
class PersonWithCensusEntries(PersonInfo):
    census_entries: Dict[str, CensusEntryInfo] = field(default_factory=dict)

people_to_export: List[PersonWithCensusEntries] = []

all_people = get_all_person_entries()
people_with_fathers = [person for person in all_people if person.parent != None]
for person in people_with_fathers:
	print(person)
	if person.parent != None:
		parent: Person = Person.get(Person.id == person.parent)
		if parent.parent == None:
			parent = personToInfo(parent)
			parent: PersonWithCensusEntries = PersonWithCensusEntries(**asdict(parent))
			parent.census_entries = get_census_entries_of_person(parent.id)
			people_to_export.append(asdict(parent))

	person = PersonWithCensusEntries(**asdict(person))
	person.census_entries = get_census_entries_of_person(person.id)
	people_to_export.append(asdict(person))

os.makedirs("./out", exist_ok=True)
with open('./out/export.json', 'w') as json_file:
	json.dump(people_to_export, json_file, indent=4)

