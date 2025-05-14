from peewee import *
from dataclasses import dataclass
from typing import Optional, List, Union

import os

os.makedirs("./out", exist_ok=True)
db = SqliteDatabase('./out/super_census.db')
db.connect()

class BaseModel(Model):
	class Meta:
		database = db

class Person(BaseModel):
	id = AutoField
	first_name = CharField(max_length=30)
	last_name = CharField(max_length=30)
	parent = ForeignKeyField('self', backref='children', null=True)

@dataclass
class PersonInfo:
	id: int
	first_name: str
	last_name: str
	parent: Optional[int] = None

def personToInfo(person: Person):
	return PersonInfo(
		id=person.id,
		first_name=person.first_name,
		last_name=person.last_name,
		parent=person.parent_id
	)

class CensusEntry(BaseModel):
	id = AutoField()
	census_year = IntegerField()
	census_page = IntegerField()
	census_row = IntegerField()
	first_name = CharField(max_length=30)
	last_name = CharField(max_length=30)
	birth_year = IntegerField(null=True)
	origin = TextField(null=True)
	job = CharField(max_length=30, null=True)
	house_nb = IntegerField(null=True)
	street_name = TextField(null=True)
	parent_census_entry = ForeignKeyField('self', backref='children', null=True)
	person = ForeignKeyField(Person, backref='census_entries', null=True)

@dataclass
class CensusEntryInfo:
	id: int
	census_year: int
	census_page: int
	census_row: int
	first_name: str
	last_name: str
	birth_year: Optional[int] = None
	origin: Optional[str] = None
	job: Optional[str] = None
	house_nb: Optional[str] = None
	street_name: Optional[str] = None
	parent_census_entry: Optional[int] = None
	person: Optional[int] = None

def censusEntryToInfo(entry: CensusEntry):
	return CensusEntryInfo(
			id=entry.id,
			census_year=entry.census_year,
			census_page=entry.census_page,
			census_row=entry.census_row,
			first_name=entry.first_name,
			last_name=entry.last_name,
			birth_year=entry.birth_year,
			origin=entry.origin,
			job=entry.job,
			house_nb=entry.house_nb,
			street_name=entry.street_name,
			parent_census_entry=entry.parent_census_entry.id if entry.parent_census_entry else None,
			person=entry.person.id if entry.person else None
		)

def reset_database():
	db.drop_tables([Person, CensusEntry], safe=True)
	db.create_tables([Person, CensusEntry])

def close_database():
	db.close()

def get_census_entries_of_person(personId: int, asCensusEntryInfo=True) -> Union[List[CensusEntry], List[CensusEntryInfo]]:
	entries = CensusEntry.select().where(CensusEntry.person == personId).execute()
	if asCensusEntryInfo:
		return [censusEntryToInfo(entry) for entry in entries]
	else:
		return [entry for entry in entries]

def get_all_census_entries(census_year: Optional[int] = None) -> List[CensusEntryInfo]:
	# Query all entries from the CensusEntry table
	entries = CensusEntry.select()
	if census_year:
		entries = entries.where(CensusEntry.census_year == census_year)

	# Convert each entry to a CensusEntryInfo dataclass
	census_entries_info = [censusEntryToInfo(entry) for entry in entries]

	return census_entries_info

def clear_and_insert_many_census_entries(census_entries: List[CensusEntryInfo]):
	def insert_many_census_entries(census_entries: List[CensusEntryInfo]):
		if len(census_entries) <= 500:
			CensusEntry.insert_many(map(lambda entry: vars(entry), census_entries)).execute()
		else:
			mid = len(census_entries) // 2
			insert_many_census_entries(census_entries[:mid])
			insert_many_census_entries(census_entries[mid:])
	CensusEntry.delete().execute()
	insert_many_census_entries(census_entries)

def insert_many_persons(persons: List[PersonInfo]):
	Person.insert_many(map(lambda person: vars(person), persons)).execute()

def get_next_person_id():
	return (Person.select(fn.MAX(Person.id)).scalar() or -1) + 1

def get_all_person_entries(asPersonInfo=True) -> Union[List[Person], List[PersonInfo]]:
	entries = Person.select().execute()
	
	if asPersonInfo:
		# Convert each entry to a PersonInfo dataclass
		return [personToInfo(entry) for entry in entries]
	else:
		return entries

if __name__ == "__main__":
	reset_database()