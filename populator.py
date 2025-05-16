import pandas as pd
from db import CensusEntryInfo, clear_and_insert_many_census_entries
from csv_fields import *
from typing import Optional, Tuple, List
from utils import *
from pathlib import Path

from fix_birth_year import estimate_birth_date

def process_entry(
	row: pd.Series, row_id: int, census_year: int
) -> Optional[Tuple[CensusEntryInfo, List[CensusEntryInfo]]]:
	if (
		pd.notna(row[FIELD_FIRST_NAME])
		and pd.notna(row[FIELD_LAST_NAME])
		and value_or_None(row[FIELD_FIRST_NAME])
		and value_or_None(row[FIELD_LAST_NAME])
	):

		def value_to_valid_age(value) -> Optional[int]:
			b_date = safe_cast_to_int(value)
			if b_date is None:
				return None
			corrected_year, leven_dis, mdfx = estimate_birth_date(b_date, census_year)
			return corrected_year if leven_dis <= 3 else None

		parent_birth_year = value_to_valid_age(row[FIELD_BIRTH_YEAR])

		parent = CensusEntryInfo(
			id=None,
			census_page=row[FIELD_PAGE],
			census_row=row_id,
			census_year=census_year,
			first_name=row[FIELD_FIRST_NAME],
			last_name=row[FIELD_LAST_NAME],
			birth_year=parent_birth_year,
			origin=value_or_None(row[FIELD_ORIGIN]),
			job=value_or_None(row[FIELD_JOB]),
			house_nb=value_or_None(row[FIELD_HOUSE_NB]),
			street_name=value_or_None(row[FIELD_STREET]),
		)

		children: List[CensusEntryInfo] = []
		if value_or_None(row[FIELD_CHILDREN_FIRST_NAMES]):
			children_first_names = row[FIELD_CHILDREN_FIRST_NAMES].split("|")
			children_birth_years = [None] * len(children_first_names)
			if row[FIELD_CHILDREN_BIRTH_YEARS] and len(children_first_names) == len(
				row[FIELD_CHILDREN_BIRTH_YEARS].split("|")
			):
				children_birth_years = row[FIELD_CHILDREN_BIRTH_YEARS].split("|")
				for i in range(len(children_birth_years)):
					children_birth_years[i] = value_to_valid_age(
						children_birth_years[i]
					)
			for i in range(len(children_first_names)):
				children.append(
					CensusEntryInfo(
						id=None,
						census_page=row[FIELD_PAGE],
						census_row=row_id,
						census_year=census_year,
						first_name=children_first_names[i],
						last_name=row[FIELD_LAST_NAME],
						birth_year=children_birth_years[i],
						origin=value_or_None(row[FIELD_ORIGIN]),
						house_nb=value_or_None(row[FIELD_HOUSE_NB]),
						street_name=value_or_None(row[FIELD_STREET]),
					)
				)

		return parent, children
	return None


def populate_database():
	census_entries: List[CensusEntryInfo] = []
	next_entry_id = 1
	for file in sorted(Path("census").iterdir()):
		if file.stem.startswith("-"):
			continue
		if file.suffix == ".csv" and safe_cast_to_int(file.stem):
			census_year = safe_cast_to_int(file.stem)
			census = pd.read_csv(file, delimiter=";", encoding='utf8')
			print(f"Processing {census_year}")

			for census_row_id, row in census.iterrows():
				entry = process_entry(row, census_row_id, census_year)
				if entry:
					parent, children = entry
					parent.id = next_entry_id
					census_entries.append(parent)
					next_entry_id += 1
					for child in children:
						child.id = next_entry_id
						child.parent_census_entry = parent.id
						next_entry_id += 1
						census_entries.append(child)

	timer = Timer("Inserting everyone to the database...")
	clear_and_insert_many_census_entries(census_entries)
	timer.tac()

if __name__ == "__main__":
	populate_database()
