import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

CATEGORY_TO_PLOT = "sector"

df = pd.read_csv("out/father_child_pairs_with_jobs.csv", sep=";")
with open("out/tracked.json", encoding='utf-8') as f:
    job_data = json.load(f)
    job_data = job_data["jobs"]

def get_job_metadata(job_ids_str, category):
    #Get all jobs of person
    job_ids = [str(job_id).strip() for job_id in str(job_ids_str).split(",")]
    metadata_list = []

    for job_id in job_ids:
        #Get job data from metadata if exists
        job_info = job_data.get(job_id)
        if job_info.get(category):
            metadata_list.append(job_info.get(category))
    return metadata_list


transition_matrix = defaultdict(lambda: defaultdict(int))

for _, row in df.iterrows():
    child_jobs = get_job_metadata(row['child_jobs'], CATEGORY_TO_PLOT)
    parent_jobs = get_job_metadata(row['parent_jobs'], CATEGORY_TO_PLOT)

    #We loop through it since parents or childs can have different jobs through the different census.
    for child_job in child_jobs:
        for parent_job in parent_jobs:
                transition_matrix[parent_job][child_job] += 1

#Create the dataframe matrix
print(transition_matrix)
all_vals = sorted(set(transition_matrix.keys()) | {k for sub in transition_matrix.values() for k in sub})
matrix_df = pd.DataFrame(index=all_vals, columns=all_vals).fillna(0)

for parent_value in all_vals:
    for child_value in all_vals:
        matrix_df.loc[parent_value, child_value] = transition_matrix[parent_value][child_value]

#Get labels and values from the matrixs
matrix = matrix_df.values
labels = matrix_df.columns.tolist()
n = len(labels)

#Compute percentages for the visualisation
row_sums = matrix.sum(axis=1, keepdims=True)
percentages = np.divide(matrix, row_sums, where=row_sums != 0) * 100

fig, ax = plt.subplots(figsize=(10, 8))
cax = ax.matshow(matrix, cmap='Blues')

for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        count = matrix[i, j]
        percent = percentages[i, j]
        if count > 0:
            ax.text(j, i, f'{count}\n({percent:.1f}%)', va='center', ha='center', fontsize=10)

# Axis labels
ax.set_xticks(np.arange(n))
ax.set_yticks(np.arange(n))
ax.set_xticklabels(labels, rotation=45, ha='left')
ax.set_yticklabels(matrix_df.index.tolist())
ax.set_xlabel("Métier de l'enfant")
ax.set_ylabel("Métier du parent")
plt.title(f"Matrice de transition parent - enfant sur toutes les données: {CATEGORY_TO_PLOT}")
fig.colorbar(cax, label='Nombre d\'individus')
plt.tight_layout()
plt.savefig(f"analysis/scatter_matrix_plots/{CATEGORY_TO_PLOT}")
plt.show()