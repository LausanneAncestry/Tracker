from db import CensusEntry, Person, CensusEntryInfo, get_all_census_entries, get_all_person_entries
from collections import defaultdict


people_found = get_all_person_entries()

def find_when_parents_before_none(lst):
    indexes = []
    for i in range(len(lst) - 1):  # Loop until the second last element
        if lst[i] is None and lst[i + 1] != None:
            indexes.append(i)
    
    return indexes if indexes else -1

def process_census_data(entry):
    persons = []
    current_person_indexes = []
    parent_id = None

    print("\nProcessing entry:", entry)  # Debugging line

    for i, p in enumerate(entry):
        print(f"Index {i}: {p}")  # Debugging line
        
        if p is None:
            current_person_indexes.append(i)
        else:
            new_parent_id = p.replace("Person: ", "") if isinstance(p, str) else p  # Keep `p` as is if not a string
            
            if parent_id is None:  
                if current_person_indexes:
                    print(f"Appending: {current_person_indexes} with parent_id=None")  # Debugging line
                    persons.append({'person_index': list(current_person_indexes), 'parent_id': None})
                parent_id = new_parent_id
                current_person_indexes = [i]
            elif parent_id == new_parent_id:
                current_person_indexes.append(i)  # Continue same group
            else:
                if current_person_indexes:
                    print(f"Appending: {current_person_indexes} with parent_id={parent_id}")  # Debugging line
                    persons.append({'person_index': list(current_person_indexes), 'parent_id': parent_id})
                parent_id = new_parent_id
                current_person_indexes = [i]

    if current_person_indexes:
        print(f"Appending (final): {current_person_indexes} with parent_id={parent_id}")  # Debugging line
        persons.append({'person_index': list(current_person_indexes), 'parent_id': parent_id})

    print("Final persons:", persons)  # Debugging line
    return persons


people_to_treat_counter = 0
for person_found in people_found:
    #get all the census entries of this person
    census_entries = CensusEntry.select().where(CensusEntry.person == person_found.id)
    #print(census_entries)

    #get all parent census entries of this person
    parent_census = [parent_id.parent_census_entry for parent_id in census_entries]
    #print(parent_census)

    #get all parent person id of this person
    parent_person_ids = []
    for parent_census_entry in parent_census:
        if parent_census_entry == None:
            parent_person_ids.append(None)
        else:
            parent_person_ids.append(parent_census_entry.person)

    #print(parent_person_ids)

    #compare parent person ids between persons      (FOR NOW ONLY GETS PEOPLE WHERE THE PARENT ID IS ALWAYS THERE!!!!!!)
    if len(set(parent_person_ids)) == 1 and parent_person_ids[0] != None:
        #check if parent is always the same
        person_to_modify_entry = Person.get(Person.id == person_found.id)
        person_to_modify_entry.parent = parent_person_ids[0].id
        person_to_modify_entry.save()
        #print("Parent is the same in all census")
    elif None not in parent_person_ids:
        #check if there is always a parent, but different parents each census
        #print("There are parents in each census, but they are different")
        pass
    elif len(set(parent_person_ids)) == 1 and parent_person_ids[0] == None:
        #there is never a parent
        #print("This person never has a parent")
        pass
    else:
        #in some census there is a parent, other ones have not
        #print(parent_person_ids)
        switch_indexes = find_when_parents_before_none(parent_person_ids)
        if switch_indexes == -1:
            #The parent comes first, and then disappears
            new_parent_person_ids = [x for x in parent_person_ids if x is not None]
            if len(set(new_parent_person_ids)) == 1 and new_parent_person_ids[0] != None:
                #check if parent is always the same
                person_to_modify_entry = Person.get(Person.id == person_found.id)
                person_to_modify_entry.parent = new_parent_person_ids[0].id
                person_to_modify_entry.save()
            elif None not in new_parent_person_ids:
                #check if there is always a parent, but different parents each census
                #print("There are parents in each census, but they are different")
                pass
        else:
            #print(person_found.id)
            #print(parent_person_ids)
            #print(switch_indexes)
            person_separations = process_census_data(parent_person_ids)
            for i, person_separated in enumerate(person_separations):
                new_person = Person.create(first_name=person_found.first_name, last_name=person_found.last_name, parent=person_separated['parent_id'])
                new_person.save()
                for census_entry_index_number in person_separated['person_index']:
                    census_entries[census_entry_index_number].person = new_person.id
                    census_entries[census_entry_index_number].save()
            #►Check if it was parent to any child!!
            print(person_found)
            old_person = Person.get(Person.id == person_found.id)
            print(old_person)
            old_person.delete_instance()

                

            

            

print(people_to_treat_counter)





    