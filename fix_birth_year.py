import Levenshtein
import pandas as pd
from typing import Optional, Tuple, List, Dict
from utils import safe_cast_to_int


def estimate_birth_date(birth_date, census_date, 
    minimum_age=5,maximum_age=90, expected_age=45):

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


def fix_birth_year(years: Dict[int, str],
                    minimum_age=0,maximum_age=100
                   ) -> Optional[int]:

    if len(years) == 1:
        census_year = years[0].key()
        birth_year = safe_cast_to_int(years[0].value())
        if birth_year is None:
            return None
        best_year, leven, proxi = estimate_birth_date(census_year, birth_year)
        return best_year

    guesses: List[int] = []
    upper_bound = 1999
    lower_bound = 1699

    for census_year, raw_year in years.items():

        lower_bound = max(census_year - maximum_age, lower_bound)
        upper_bound = min(census_year - minimum_age, upper_bound)

        candidates = [int(year) for year in str(raw_year).split('|')]
        if len(candidates) == 1:
            guesses.extend(candidates)
        else:
            pass 
            # annoying "1802 | 1796" are ignored

    if lower_bound > upper_bound:
        return None

    min_error = float('inf')
    for candidate in range(lower_bound, upper_bound + 1):
        error = sum(Levenshtein.distance(str(candidate), str(guess)) for guess in guesses)
        if error < min_error:
            min_error = error
            best_year = candidate
    return best_year


    




def test_find():
    date = fix_birth_year({1835 : 1832, 1855 : 1802})
    print(date)

    print(fix_birth_year({1810 : "1798 | 1802", 1820 : "805", 1830 : "1805", 1840: "41806"}))



def test_estimate():
    # Read the CSV file
    filename = 'census/1835.csv'
    census_date = 1835

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
