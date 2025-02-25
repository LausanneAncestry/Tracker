from db import reset_database, close_database
from populator import populate_database
from tracker import track_persons

def main():
	reset_database()
	populate_database()
	track_persons()
	close_database()

if __name__ == "__main__":
	main()