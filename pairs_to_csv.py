from db import CensusEntry, Person, CensusEntryInfo, get_all_census_entries, get_all_person_entries
import pandas as pd

data = {
    "father_first_name": [],
    "father_last_name": [],
    "father_id": [],
    "father_job": [],
    "father_census_entries": [],
    "son_first_name": [],
    "son_last_name": [],
    "son_id": [],
    "son_job": [],
    "son_census_entries": []
}

all_entries = get_all_census_entries(adults=False, children=False)
all_people = get_all_person_entries()
people_with_fathers = [person for person in all_people if person.parent != None]

for person in people_with_fathers:
    persons_parent = None
    for parent in all_entries:
        if parent.id == person.parent:
            persons_parent = parent
    data["son_first_name"].append(person.first_name)
    data["son_last_name"].append(person.last_name)
    data["son_id"].append(person.id)
    data["father_first_name"].append(persons_parent.first_name)
    data["father_last_name"].append(persons_parent.last_name)
    data["father_id"].append(persons_parent.id)
    son_census_entries = [entry for entry in all_entries if entry.person == person.id]
    father_census_entries = [entry for entry in all_entries if entry.person == person.parent]
    data["father_job"].append(set([entry.job for entry in father_census_entries if entry.job is not None]))
    data["father_census_entries"].append([entry.id for entry in father_census_entries])
    data["son_census_entries"].append([entry.id for entry in son_census_entries])
    data["son_job"].append(set([entry.job for entry in son_census_entries if entry.job is not None]))

print(data)

dataframe = pd.DataFrame(data)
dataframe.to_csv("csv_paires.csv", sep=";")