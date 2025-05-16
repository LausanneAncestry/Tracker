from db import CensusEntry, Person, get_all_person_entries, get_census_entries_of_person
from typing import List, Optional
from utils import Timer

def find_parents_before_none(parents: List[int]):
	indexes = []
	for i in range(len(parents) - 1):  # Loop until the second last element
		if parents[i] is None and parents[i + 1] != None:
			indexes.append(i)
	return indexes

def find_different_persons_in_same_entry(entry):
	persons = []
	current_person_indexes = []
	parent_id = None

	for i, p in enumerate(entry):

		if p is None:
			current_person_indexes.append(i)
		else:
			new_parent_id = p.replace("Person: ", "") if isinstance(p, str) else p  # Keep `p` as is if not a string
			
			if parent_id is None:  
				if current_person_indexes:
					persons.append({'person_index': list(current_person_indexes), 'parent_id': None})
				parent_id = new_parent_id
				current_person_indexes = [i]
			elif parent_id == new_parent_id:
				current_person_indexes.append(i)  # Continue same group
			else:
				if current_person_indexes:
					persons.append({'person_index': list(current_person_indexes), 'parent_id': parent_id})
				parent_id = new_parent_id
				current_person_indexes = [i]

	if current_person_indexes:
		persons.append({'person_index': list(current_person_indexes), 'parent_id': parent_id})

	return persons

def post_tracking():
	timer = Timer(f"Starting post tracking...")
	people_found: List[Person] = get_all_person_entries(asPersonInfo=False)
	people_changed: dict = {}

	print("Add parents who are not considered as persons yet to the database")
	# Make the query again for potential changes in the db
	people_found: List[Person] = get_all_person_entries(asPersonInfo=False)
	for person in people_found:
		census_entries: List[CensusEntry] = get_census_entries_of_person(person.id, asCensusEntryInfo=False)
		for entry in census_entries:
			if entry.parent_census_entry != None:
				parent_entry = CensusEntry.select().where(CensusEntry.id == entry.parent_census_entry)

				# Si le parent n'est pas une personne:
				# L'ajouter en tant que personne a la db
				# Ajouter la nouvelle personne id a l'enfant
				if parent_entry[0].person == None:
					# Create new instances for the parent
					new_person_parent = Person.create(first_name=parent_entry[0].first_name, last_name=parent_entry[0].last_name, parent=parent_entry[0].parent_census_entry)
					new_person_parent.save()
					for parent_census_entry in parent_entry:
						parent_census_entry.person = new_person_parent.id
						parent_census_entry.save()
					person.parent = new_person_parent.id
					person.save()
				break

	print("Adding parents to Person")
	for person in people_found:
		census_entries: List[CensusEntry] = get_census_entries_of_person(person.id, asCensusEntryInfo=False)
		parent_census_entries: List[Optional[CensusEntry]] = [parent_id.parent_census_entry for parent_id in census_entries]
		parent_ids = []
		for parent_census_entry in parent_census_entries:
			if parent_census_entry == None:
				parent_ids.append(None)
			else:
				#TODO: Removes all parents that do not have a person.id --> Create them if they do not have them
				parent_ids.append(parent_census_entry.person_id)		
		
		""" # Everything is good, nothing to do
		if len(set(parent_ids)) == 1 and parent_ids[0] != None: 
			person.parent = parent_ids[0]
			# TODO: add birthyear here
			# person.birth_year = ???
			person.save() """

		# This person doesn't have a parent, we don't track them
		if len(set(parent_ids)) == 1 and parent_ids[0] == None:
			pass
			
		# In some census there is a parent, other ones have not
		else:
			separated_persons = find_different_persons_in_same_entry(parent_ids)

			# The parent comes first, then disappears. We don't need to create new instances of Person
			if len(separated_persons) == 1:
				person.parent = separated_persons[0]['parent_id']
				# TODO: add birthyear here
				# person.birth_year = ???
				person.save()
			
			else:
				people_changed[person.id] = []
				for dif_person in separated_persons:
					# Create new instances for each person
					new_person = Person.create(first_name=person.first_name, last_name=person.last_name, parent=person.parent)
					# TODO: add birthyear here
					# person.birth_year = ???
					new_person.save()

					# Track changes for later check on all instances
					people_changed[person.id].append(new_person.id)
					
					# Change values from their census entries to match the new indexes
					for index in dif_person['person_index']:
						census_entries[index].person = new_person.id
						census_entries[index].save()	

	print("Delete deprecated instances of duplicated persons")
	# Delete old instances of duplicated people:
	for person_id in people_changed.keys():
		person_to_delete = Person.select().where(Person.id == person_id)[0]
		person_to_delete.delete_instance()

	print("Update parent indexes for childs with duplicated parents")
	# Make the query again for potential changes in the db
	people_found: List[Person] = get_all_person_entries(asPersonInfo=False)
	# Check and change the missing indexes of separated persons in their child's parent_id:
	for person in people_found:
		try:
			if person.parent == None:
				continue
		except:
			census_entries: List[CensusEntry] = get_census_entries_of_person(person.id, asCensusEntryInfo=False)
			parent_was_found = False
			for entry in census_entries:
				if entry.parent_census_entry != None:
					parent_entry = CensusEntry.select().where(CensusEntry.id == entry.parent_census_entry)[0]
					person.parent = parent_entry.person	
					person.save()
					parent_was_found = True
					break
			
			# If it didn't change we default to None
			if not parent_was_found:
				person.parent = None

	timer.tac()

if __name__ == "__main__":
	post_tracking()