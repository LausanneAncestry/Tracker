from db import CensusEntry, Person, get_all_person_entries, get_census_entries_of_person

from typing import List, Optional
from utils import Timer

def find_parents_before_none(parents: List[int]):
	indexes = []
	for i in range(len(parents) - 1):  # Loop until the second last element
		if parents[i] is None and parents[i + 1] != None:
			indexes.append(i)
	return indexes

def post_tracking():
	timer = Timer(f"Starting post tracking...")
	people_found: List[Person] = get_all_person_entries(asPersonInfo=False)
	
	for person in people_found:
		census_entries: List[CensusEntry] = get_census_entries_of_person(person.id, asCensusEntryInfo=False)
		parent_census_entries: List[Optional[CensusEntry]] = [parent_id.parent_census_entry for parent_id in census_entries]
		parent_ids = []
		for parent_census_entry in parent_census_entries:
			if parent_census_entry == None:
				parent_ids.append(None)
			else:
				parent_ids.append(parent_census_entry.person_id)
		
		# Everything is good, nothing to do
		if len(set(parent_ids)) == 1 and parent_ids[0] != None: 
			person.parent = parent_ids[0]
			# TODO: add birthyear here
			# person.birth_year = ???
			person.save()

		# This person doesn't have a parent, we don't track they
		elif len(set(parent_ids)) == 1 and parent_ids[0] == None:
			pass

		# There are parents in each census, but they are different
		elif None not in parent_ids:
			pass

		# In some census there is a parent, other ones have not
		else:
			index_of_first_missing_parent = parent_ids.index(None)

			if index_of_first_missing_parent > 0:
				ends_with_nones = all(e is None for e in parent_ids[index_of_first_missing_parent:])
				
				# The parent comes first, and then disappears
				if ends_with_nones:
					parent_ids = parent_ids[:index_of_first_missing_parent]
					
					# Everything is good, nothing to do
					if len(set(parent_ids)) == 1:
						person.parent = parent_ids[0]
						# TODO: add birthyear here
						# person.birth_year = ???
						person.save()
				
					# There are parents in each census, but they are different
					else:
						pass
				
				# It's a french Gruyère, what can we do ?
				else:
					pass

			# We start with a missing parent => it's a mistake
			else:
				# TODO
				pass
			
	timer.tac()

if __name__ == "__main__":
	post_tracking()