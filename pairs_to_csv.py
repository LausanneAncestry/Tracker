import json
import csv
import pandas as pd

with open("out"+"/"+"tracked.json", "r", encoding="utf-8") as f:
    data = json.load(f)

persons = data["persons"]

person_by_id = {person["id"]: person for person in persons}

#Get valid jobs (10019 is no vocation and -1 is emploi inconnu so don't take them)
def get_valid_jobs(job_ids):
    return [job_id for job_id in job_ids if job_id not in [10019, -1]]

#Find child/parent pairs who both have valid jobs
pairs = []

for person in persons:
    #Get parent id if it exists
    parent_id = person.get("parent")
    if parent_id is None:
        continue

    #Check if parent exists
    parent = person_by_id.get(parent_id)
    if not parent:
        continue

    child_jobs = set(get_valid_jobs(person["job_ids"]))
    parent_jobs = set(get_valid_jobs(parent["job_ids"]))

    if child_jobs and parent_jobs:
        pairs.append({
            "child_id": person["id"],
            "child_name": f'{person["first_name"]} {person["last_name"]}',
            "child_jobs": ','.join(map(str, child_jobs)),
            "parent_id": parent["id"],
            "parent_name": f'{parent["first_name"]} {parent["last_name"]}',
            "parent_jobs": ','.join(map(str, parent_jobs)),
        })

df = pd.DataFrame(pairs)
df.to_csv("out\\father_child_pairs_with_jobs.csv", sep=';', encoding='utf-8', index=False)