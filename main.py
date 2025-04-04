from db import reset_database, close_database
from populator import populate_database
from tracker import track_persons

def main():
	reset_database()
	populate_database()
	track_persons()
	close_database()
	# run manually check_if_same_person_but_better
	# run manually pairs_to_csv -> generates 'csv_paires.csv'
	# run clean_jobs (Yao's code: should add 'standardised_job' columns)
	# run extract_relevant_jobs -> generates 'relevant_jobs.csv'


if __name__ == "__main__":
	main()