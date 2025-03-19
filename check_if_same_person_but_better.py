from db import CensusEntry, Person, CensusEntryInfo, get_all_census_entries, get_all_person_entries

people_found = get_all_person_entries()

def find_when_parents_before_none(lst):
    indexes = []
    for i in range(len(lst) - 1):  # Loop until the second last element
        if lst[i] is None and lst[i + 1] != None:
            indexes.append(i)
    
    return indexes if indexes else -1


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
            print(person_found.id)
            print(parent_person_ids)
            print(switch_indexes)
            people_to_treat_counter += 1
            #loop through switch indexes:
            for index in switch_indexes:
                #all entries up to index are the same person
                #if there is None before Person --> no parent then parent so different person
                pass

print(people_to_treat_counter)





    