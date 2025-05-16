import pandas as pd
from db import CensusEntry, Person, CensusEntryInfo, get_all_person_entries
import numpy as np

all_census_entries = pd.DataFrame(get_all_person_entries())

chosen_entries = np.random.choice(all_census_entries.shape[0], replace=False, size=50)
chosen_entries = all_census_entries.iloc[chosen_entries]

ocr_evaluation = pd.read_csv("model_evaluation\\pairs_evaluation.csv", sep=";", encoding='utf8')

a = ocr_evaluation.shape[0]
for i, entry in chosen_entries.iterrows():
    new_row = [entry["id"], entry["first_name"],entry["last_name"], None,None,None]
    ocr_evaluation.loc[a] = new_row
    a += 1


print(ocr_evaluation)
ocr_evaluation.to_csv("model_evaluation\\pairs_evaluation.csv",sep=";", encoding='utf8')