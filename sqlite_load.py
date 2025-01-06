import sqlite_utils

from util.file_utils import create_incremented_filename

db=None

def add_to_sqlite(jobs_array):
    global db
    connect_to_db()
    for json_data in jobs_array:
        # Remove fields that are not in the database schema
        if 'isNotInteresting' in json_data:
            del json_data['isNotInteresting']
            
        # Insert the JSON data into a table (creating the table if necessary)
        # The nested JSON (like 'job_details', 'footer_info', 'analysis') will be stored as JSON blobs
        db["jobs"].insert(json_data, pk="job_id")
        print(json_data)

    # Define the SQL query to extract `years_of_experience` from `analysis.Resume`
    # query = """
    #     SELECT json_extract(analysis, '$.Overall.similarity') AS similarity
    #     FROM jobs;
    # """
    #
    # # Execute the query
    # results = db.query(query)

    # Iterate through the results and print the extracted experience
    # for row in results:
    #     print("Similarity:", row["similarity"])


def connect_to_db():
    global db
    if not db:
        # Connect to a new or existing SQLite database
        base_filename = "linkedIn_App/linkedIn_Analysis.db"
            #"linkedIn_App/my_database_4.db"

        db_path = base_filename
        # db_path = create_incremented_filename(base_filename)
        print(f"Connecting to db {db_path}")
        db = sqlite_utils.Database(db_path)
        # db = sqlite_utils.Database(memory=True)



def job_id_in_database(job_id):
    global db
    connect_to_db()
    if not "jobs" in db.table_names():
        return False
    query = """
            SELECT *
            FROM jobs
            WHERE job_id = ?;
        """

    # Execute the query and convert results to a list
    results = list(db.query(query, [job_id]))

    # Count the number of rows returned
    num_rows = len(results)

    if num_rows > 0:
        print(f"{num_rows} rows found for job_id={job_id}")
        return True
    else:
        print(f"No existing rows found for job_id={job_id}")
        return False

