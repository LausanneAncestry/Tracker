import pandas as pd
import unicodedata
from rapidfuzz import fuzz
import ast
THRESHOLD=80

# Define constants
# YEAR = '1810'  # Change this to read different year files
# RECENS_DIR = 'recensements'  # Directory containing the CSV files
RECENS_FILE = f'../csv_paires.csv'  # Path to the recens file
ALL_METIERS_FILE = f'all_metiers1.csv'  # Path to the all_metiers file
OUTPUT_FILE = f'withjobid1.csv'  # Output file name
UNMATCHED_OUTPUT_FILE = f'unmatch1.txt'  # File to save unmatched items
NAMEOFROW='father_job'
NAMEOFOUTPUT='father_job_id'

# Load CSV files
recens = pd.read_csv(RECENS_FILE, delimiter=';')
all = pd.read_csv(ALL_METIERS_FILE)


# If the first column is an index column (Unnamed: 0), set it as the index
if 'Unnamed: 0' in all.columns:
    all.set_index('Unnamed: 0', inplace=True)
    all.index.name = None  # Remove the index column name

# Rename the 'titre' column to 'word'
all.columns = ['titre']

# Function to normalize strings
def normalize_string(s):
    if not isinstance(s, str):
        return ''
    # Remove spaces and special characters
    s = ''.join(c for c in s if c.isalnum())
    # Normalize accented characters to their base form
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return s.lower()


# Normalize the 'titre' column in the 'all' table
all['normalized_titre'] = all['titre'].apply(normalize_string)

# Expand synonyms in 'all' dataframe
expanded_rows = []
for index, row in all.iterrows():
    synonyms = row['titre'].split('|')  # Split multiple synonyms
    for synonym in synonyms:
        expanded_rows.append({'index': index, 'titre': synonym.strip(), 'normalized_titre': normalize_string(synonym.strip())})

# Convert expanded rows into DataFrame
all_expanded = pd.DataFrame(expanded_rows)


# Function for fuzzy matching
def fuzzy_match(term, choices, threshold=THRESHOLD):
    best_match = None
    best_score = 0
    for choice in choices:
        score = fuzz.ratio(term, choice)
        if score > best_score:
            best_score = score
            best_match = choice
    if best_score >= threshold:
        return best_match, best_score
    return None, 0


# Initialize lists to store unmatched and fuzzy-matched items
unmatched_items = []
fuzzy_matched_items = []

# Process the 'chef_vocation' column in the 'recens' table
recens[NAMEOFOUTPUT] = None
for index, row in recens.iterrows():
    # Check if the value is NaN (missing value)
    if pd.isna(row[NAMEOFROW]):
        terms = []  # If missing, set terms to an empty list
    else:
        terms = list(ast.literal_eval(row[NAMEOFROW]))  # Split multiple terms by '|'
    matched_ids = []  # Store matched IDs
    unmatched_terms = []  # Store unmatched terms

    for term in terms:
        # If the term is '·', directly assign '·' as the ID
        if term.strip() == '·' or term.strip() == '?' or term.strip() == '.' or term.strip() == '':
            matched_ids.append('·')
            continue

        normalized_term = normalize_string(term)

        # Try exact match
        match = all_expanded[all_expanded['normalized_titre'] == normalized_term]
        if not match.empty:
            matched_ids.append(str(match.iloc[0]['index']))  # Use the original index as the ID
            continue

        # Try fuzzy match
        best_match, best_score = fuzzy_match(normalized_term, all_expanded['normalized_titre'])
        if best_match:
            match = all_expanded[all_expanded['normalized_titre'] == best_match]
            matched_ids.append(str(match.index[0]))  # Use the index as the ID
            fuzzy_matched_items.append({
                'row_index': index,
                'original_term': term,
                'matched_term': best_match,
                'score': best_score
            })
            continue
        # Special cases
        if 'secretaire' in term.lower():
            matched_ids.append('10089')
            continue
        if 'marchand' in term.lower():
            matched_ids.append('6950')
            continue
        if 'fabriqu' in term.lower():
            matched_ids.append('8354')
            continue
        if 'garde' in term.lower():
            matched_ids.append('5545')
            continue
        if 'juge' in term.lower():
            matched_ids.append('6601')
            continue
        if 'emp' in term.lower():
            matched_ids.append('4171')
            continue
        if 'fab' in term.lower():
            matched_ids.append('8354')
            continue
        # If still no match, add '?' to the matched_ids
        matched_ids.append('?')
        unmatched_terms.append(term)

    # Join matched IDs with '|' and assign to the 'metier_id' column
    recens.at[index, NAMEOFOUTPUT] = "{" + ",".join(matched_ids) + "}"

    # If there are unmatched terms, record the row information
    if unmatched_terms:
        unmatched_items.append({
            'row_index': index,
            'row_data': row.to_dict(),
            'unmatched_terms': unmatched_terms
        })

# Ensure the 'metier_id' column is of string type
recens[NAMEOFOUTPUT] = recens[NAMEOFOUTPUT].astype(str)

# Save the result as a semicolon-separated CSV file
recens.to_csv(OUTPUT_FILE, sep=';', index=False)

# Count the number of unmatched terms
unmatched_count = sum(len(item['unmatched_terms']) for item in unmatched_items)
print(f"Total number of unmatched terms: {unmatched_count}")

# Save unmatched items to a text file
if unmatched_items:
    with open(UNMATCHED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("The following items were not matched successfully:\n")
        for item in unmatched_items:
            f.write(f"Row number: {item['row_index']}\n")
            f.write(f"chef_vocation: {item['row_data'][NAMEOFROW]}\n")
            f.write(f"Unmatched terms: {'|'.join(item['unmatched_terms'])}\n")
            f.write("-" * 40 + "\n")
        f.write(f"Total number of unmatched terms: {unmatched_count}\n")
    print(f"Unmatched items have been saved to {UNMATCHED_OUTPUT_FILE}")
else:
    print("No unmatched items to save.")