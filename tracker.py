from db import CensusEntry, Person, CensusEntryInfo, get_all_census_entries
from peewee import fn
from dataclasses import dataclass
from typing import List, Tuple
from utils import Timer, are_close_enough

@dataclass
class TrackingSummary:
    first_year: int
    second_year: int
    size_of_first_year: int
    size_of_second_year: int
    number_of_ambiguities: int
    number_of_tracked_people: int
    tracked_entries: Tuple[CensusEntryInfo, CensusEntryInfo]

    def __str__(self):
        return (
            f"TrackingSummary(first_year={self.first_year}, "
            f"second_year={self.second_year}, "
            f"size_of_first_year={self.size_of_first_year}, "
            f"size_of_second_year={self.size_of_second_year}, "
            f"number_of_ambiguities={self.number_of_ambiguities}, "
            f"number_of_tracked_people={self.number_of_tracked_people})"
        )


def get_unique_census_years():
    unique_years = CensusEntry.select(fn.DISTINCT(CensusEntry.census_year)).tuples()
    return sorted([year[0] for year in unique_years])


def find_person(
    person: CensusEntryInfo, people: List[CensusEntryInfo]
) -> List[CensusEntryInfo]:
    candidates: List[CensusEntryInfo] = []
    for candidate in people:
        if are_close_enough(person.last_name, candidate.last_name) and are_close_enough(
            person.first_name, candidate.first_name
        ):
            if person.first_name != candidate.first_name + 'e' and candidate.first_name != person.first_name + 'e':
                if person.origin == None or are_close_enough(person.origin, candidate.origin):
                    candidates.append(candidate)
    if len(candidates) == 1:
        return [candidates[0]]

    if len(candidates) > 1:
        """ if person.origin != None:
            candidates_with_same_origin: List[CensusEntryInfo] = []
            for candidate in candidates:
                if are_close_enough(person.origin, candidate.origin):
                    candidates_with_same_origin.append(candidate)
            if len(candidates_with_same_origin) == 1:
                return candidates_with_same_origin
            elif len(candidates_with_same_origin) > 1:
                candidates = candidates_with_same_origin """

        if person.birth_year != None:
            candidates_with_same_birth_year: List[CensusEntryInfo] = []
            for candidate in candidates:
                if person.birth_year == candidate.birth_year:
                    candidates_with_same_birth_year.append(candidate)
            if len(candidates_with_same_birth_year) == 1:
                return candidates_with_same_birth_year
            elif len(candidates_with_same_birth_year) > 1:
                candidates = candidates_with_same_birth_year

        if person.street_name != None:
            candidates_with_same_street: List[CensusEntryInfo] = []
            for candidate in candidates:
                if are_close_enough(person.street_name, candidate.street_name):
                    candidates_with_same_street.append(candidate)
            if len(candidates_with_same_street) == 1:
                return candidates_with_same_street
            elif len(candidates_with_same_street) > 1:
                candidates = candidates_with_same_street
    return candidates


def track_persons_between_2_census(
    first_census: List[CensusEntryInfo], second_census: List[CensusEntryInfo]
) -> TrackingSummary:
    if len(first_census) == 0 or len(second_census) == 0:
        raise Exception("Empty census")

    first_year = first_census[0].census_year
    second_year = second_census[0].census_year

    timer = Timer(
        f"Starting tracking between {first_year} and {second_year} ({len(first_census)} and {len(second_census)} entries)"
    )

    first_year_not_matched_people = list(first_census)
    second_year_not_matched_people = list(second_census)

    number_of_ambiguities = 0
    tracked_entries: List[Tuple[CensusEntryInfo, CensusEntryInfo]] = []

    improvement = True
    while improvement:
        improvement = False

        number_of_ambiguities = 0
        first_year_people_for_next_pass = []
        for first_year_person in first_year_not_matched_people:
            candidates = find_person(first_year_person, second_year_not_matched_people)
            if len(candidates) > 1:
                number_of_ambiguities += 1
                first_year_people_for_next_pass.append(first_year_person)
            elif len(candidates) == 1:
                candidate = candidates[0]
                tracked_entries.append((first_year_person, candidate))
                second_year_not_matched_people.remove(candidate)
                improvement = True

        first_year_not_matched_people = first_year_people_for_next_pass

    timer.tac("Tracking done in {TIME}")

    return TrackingSummary(
        first_year=first_year,
        second_year=second_year,
        size_of_first_year=len(first_census),
        size_of_second_year=len(second_census),
        number_of_ambiguities=number_of_ambiguities,
        number_of_tracked_people=len(tracked_entries),
        tracked_entries=tracked_entries,
    )


def track_persons():
    census_years = get_unique_census_years()
    if len(census_years) < 2:
        raise Exception("Not enough years")

    for year_index in range(len(census_years) - 1):
        current_year = census_years[year_index]
        next_year = census_years[year_index + 1]

        tracking_summary = track_persons_between_2_census(
            get_all_census_entries(census_year=current_year),
            get_all_census_entries(census_year=next_year),
        )
        print(tracking_summary)
        for first_entry, second_entry in tracking_summary.tracked_entries:
            if first_entry.person == None:
                first_entry.person = Person.create(
                    first_name=first_entry.first_name, last_name=first_entry.last_name
                )
                CensusEntry.update(person=first_entry.person).where(
                    CensusEntry.id == first_entry.id
                ).execute()
            second_entry.person = first_entry.person
            CensusEntry.update(person=second_entry.person).where(
                CensusEntry.id == second_entry.id
            ).execute()


if __name__ == "__main__":
    track_persons()