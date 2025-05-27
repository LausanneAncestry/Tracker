import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


PARENT_JOB = "rentier"

df = pd.read_csv("out/father_child_pairs_with_jobs.csv", sep=";")
with open("out/tracked.json", encoding='utf-8') as f:
    job_data = json.load(f)
    job_data = job_data["jobs"]
    job_name = {str(k): v['job'] for k, v in job_data.items() if 'job' in v}

#Explode rows with several jobs
df['child_jobs'] = df['child_jobs'].str.split(',')
df = df.explode('child_jobs').reset_index(drop=True)
df['parent_jobs'] = df['parent_jobs'].str.split(',')
df = df.explode('parent_jobs').reset_index(drop=True)

df['parent_jobs'] = df['parent_jobs'].replace(job_name)
df['child_jobs'] = df['child_jobs'].replace(job_name)

job_parent_only = df.groupby("parent_jobs").size().reset_index(name='count')
job_parent_only = job_parent_only.sort_values(by='count', ascending=False)
print("Most common jobs held by the parents:")
print(job_parent_only.head(10))

job_pairs = df.groupby(['parent_jobs', 'child_jobs']).size().reset_index(name='count')
job_pairs = job_pairs.sort_values(by='count', ascending=False)

print("--------------------------")
print("Most common pairs")
print(job_pairs.head(20))

job_pairs = job_pairs[job_pairs["parent_jobs"] == PARENT_JOB]

#List of all unique jobs
all_jobs = list(pd.unique(job_pairs[['parent_jobs', 'child_jobs']].values.ravel()))

#Mapping for Sankey diagram
job_to_id = {job: i for i, job in enumerate(all_jobs)}
job_pairs['source'] = job_pairs['parent_jobs'].map(job_to_id)
job_pairs['target'] = job_pairs['child_jobs'].map(job_to_id)

# Build the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=all_jobs,
        color="skyblue"
    ),
    link=dict(
        source=job_pairs['source'],
        target=job_pairs['target'],
        value=job_pairs['count']
    ))])

fig.show()