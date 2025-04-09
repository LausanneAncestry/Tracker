import pandas as pd
import unicodedata
from rapidfuzz import fuzz
import ast
import re

import pandas as pd

# Read input CSV file
list = pd.read_csv(f'../csv_paires_jobnorm.csv', delimiter=';')
CO1 = 'father_job_norm'
CO2 = 'son_job_norm'
OUTPUT = f'../dictionnaire_job.csv'

output_data = []

# Function to process elements
def process_elements(elements):
    if isinstance(elements, str):
        elements = elements.strip("{}").split(',')
        elements = [elem.strip("'") for elem in elements]
        return [elem for elem in elements if elem not in ['?', '·'] and elem]  # Remove empty and unwanted elements
    return []

# Iterate over each row in the input DataFrame
for index, row in list.iterrows():
    co1_elements = row[CO1]
    co2_elements = row[CO2]

    # Process the elements
    co1_processed = process_elements(co1_elements)
    co2_processed = process_elements(co2_elements)

    # Append the processed words to the output_data list
    output_data.extend(co1_processed + co2_processed)

# Remove duplicates by converting to a set, then sort in lexicographical order
unique_sorted_words = sorted(set(output_data))

# Create the output DataFrame with row numbers
output_list = pd.DataFrame(unique_sorted_words, columns=['Word'])
output_list.reset_index(drop=False, inplace=True)  # Reset index and keep it as a column
output_list['Index'] = output_list.index + 1  # Adjust index to start from 1

# Reorder columns so that the first column is the 'Index'
output_list = output_list[['Index', 'Word']]

# Save to CSV
output_list.to_csv(OUTPUT, sep=';', index=False)
