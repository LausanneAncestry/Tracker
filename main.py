from db import reset_database, close_database
from populator import populate_database
from tracker import track_persons
from post_tracking import post_tracking
from json_export import json_export

from utils import Timer

def main():
	timer = Timer()
	reset_database()
	populate_database()
	track_persons()
	post_tracking()
	json_export()
	close_database()

	timer.tac("Finished in {TIME}")
	# run manually pairs_to_csv -> generates 'csv_paires.csv'
	# run clean_jobs (Yao's code: should add 'standardised_job' columns)
	# run extract_relevant_jobs -> generates 'relevant_jobs.csv'


if __name__ == "__main__":
	main()