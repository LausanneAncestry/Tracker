import Levenshtein
import pandas as pd

def estimate_birth_date(birth_date, census_date, 
    minimum_age=5,maximum_age=90, expected_age=40):

    earliest = census_date - maximum_age
    latest = census_date - minimum_age
    expected = census_date - expected_age

    def is_valid_year(year):
        return earliest <= year <= latest

    THRESHOLD = 2

    if is_valid_year(birth_date):
        return birth_date, 0, 0
    else:
        min_distance = float('inf')
        min_diff_from_expected = float('inf')
        best_year = expected

        for year in range(earliest, latest + 1):
            distance = Levenshtein.distance(str(year), str(birth_date))
            diff_from_expected = abs(year - expected)

            if distance <= THRESHOLD:
                if distance < min_distance or (distance == min_distance and diff_from_expected < min_diff_from_expected):
                    min_distance = distance
                    min_diff_from_expected = diff_from_expected
                    best_year = year

        return best_year, min_distance, min_diff_from_expected

# Read the CSV file
filename = 'recensements/1845.csv'
census_date = 1845

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(filename, encoding='utf-8', delimiter=';')

# Process each row in the DataFrame
for index, row in df.iterrows():
    birth_date_str = row['chef_annee_naissance']
    
    try:
        birth_date = int(birth_date_str)
    except ValueError:
        # print(f"Invalid birth date: {birth_date_str}")
        continue

    corrected_date, levenshtein_dist, diff_to_expected = estimate_birth_date(birth_date, census_date)

    if levenshtein_dist > 0:

        print(f"Original birth date: {birth_date}")
        print(f"Corrected birth date: {corrected_date}")
        print(f"Levenshtein distance: {levenshtein_dist}")
        print(f"Difference to expected value: {diff_to_expected}")
        print("---")
