import requests
import os
import sys
import time
import argparse
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import URL, create_engine

'''
	Gets the data from the url and writes to a local file to the script location 
	directory. This file will be deleted after script completion
		* url: url to get the data from
		* output_fname: output filename to write the data to

'''
def get_data_from_source(url, output_fname):
	response = requests.get(url, stream=True) # Stream file with requests to avoid loading all in memory
	if response.status_code == 200: # Only continue if we have a successful request
		with open(output_fname, 'wb') as out: # Open a file to write results to
			for resp in response.iter_content(chunk_size=500000): # Stream in 5mb chunks
				if resp: # Handle end cases/missing chunks
					out.write(resp)
		print('Local copy of data successfully written!')
	else:
		print(f'Error encountered downloading data! {response.status_code}')
		sys.exit()

'''
	Writes data obtained from parquet/csv URL to postgres SQL instance
		* engine: sqlalchemy engine for database connection
		* filename: local file to read data from
		* tablename: tablename to write to in postgres db
'''
def write_data_to_sql(engine, filename, table_name):
	if '.parquet' in filename: # Load parquet file in chunks
		data = pq.ParquetFile(filename)
		batches = data.iter_batches(batch_size=100000)
	else: # Load csv file in chunks
		batches = pd.read_csv(filename, iterator=True, chunksize=100000)

	# Start time
	init_time = time.time()

	# Iterate over all batches
	with engine.connect() as conn:
		for idx, batch in enumerate(batches):
			if '.parquet' in filename: # Convert to pandas for parquet
				batch = batch.to_pandas()
			if idx == 0: # Run create table statement
				batch.head(0).to_sql(name=table_name, con=conn, if_exists='replace', index=False)
			print(f'Writing batch {str(idx + 1)}')
			start_time = time.time() # Start time of write
			batch.to_sql(name=table_name, con=conn, if_exists='append', index=False) # Write batch and append to result
			total_time = time.time() - start_time # Time to write batch
			print(f'Batch {str(idx + 1)} completed in {str(round(total_time, 3))} seconds')
	
	# Write out total completion time
	print(f'Completed write in {str(round(time.time() - init_time, 3))} seconds')

	# Delete tmp file
	os.remove(filename)

'''
	Executes a call to ingest data from a parquet/csv url to postgres
		* args: input containing arguments passed to scrip; all are required inputs
'''
def execute_script(args):
	user = args.user # postgres username
	password = args.password # postgres password
	host = args.host # host used for postgres server
	port = args.port # port used for postgres
	db = args.db # postgres database being written to
	tb = args.tb # tablename where data is being written to
	url = args.url # url for the parquet/csv file

	# Create engine
	pg_URL = URL.create(
		drivername='postgresql', # Driver to use
		username=user, # Username of login
		password=password, # Password of login
		host=host, # Host for login
		port=port, # Connection port
		database=db # Database for connection
	)
	pg_engine = create_engine(pg_URL)

	# URL must be a parquet or csv
	if '.parquet' not in url and '.csv' not in url:
		print('Error! Input file must be a .parquet or .csv')
		sys.exit()

	# Create temp file name
	fname = './tmp.parquet' if '.parquet' in url else './tmp.csv'

	# Write data to tmp file
	get_data_from_source(url, fname)

	# Write data to database
	write_data_to_sql(pg_engine, fname, tb)

if __name__ == "__main__":
	# Set up argument parser
	parser = argparse.ArgumentParser(
		description='Loading data from parquet/csv input file link to a Postgres datebase.'
	)

	# Add arguments
	parser.add_argument('--user', help='Username for Postgres.')
	parser.add_argument('--password', help='Password to the username for Postgres.')
	parser.add_argument('--host', help='Hostname for Postgres.')
	parser.add_argument('--port', help='Port for Postgres connection.')
	parser.add_argument('--db', help='Databse name for Postgres')
	parser.add_argument('--tb', help='Destination table name for Postgres.')
	parser.add_argument('--url', help='URL for paraquet/csv file.')
	
	# Extract arguments from input
	args = parser.parse_args()

	# Execute the script
	execute_script(args)
