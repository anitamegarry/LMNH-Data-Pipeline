"""Pipeline"""

import boto3
import os
import csv
import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import logging
import sys
import argparse

from dotenv import load_dotenv
from botocore.exceptions import ClientError
from extract import (get_client,
                     check_bucket_exists, download_files, combine_csv_files,
                     delete_individual_csv_files)

load_dotenv()


def get_connection() -> connection:
    "Gets connection to database"
    return psycopg2.connect(database=os.getenv("db_name"),
                            user=os.getenv("db_user"),
                            host=os.getenv("db_host"),
                            password=os.getenv("db_password"))


def get_cursor(conn: connection) -> cursor:
    "Gets cursor"
    return conn.cursor(cursor_factory=RealDictCursor)


def upload_data_to_database(row_limit: int = None):
    """Uploads data from csv to database"""
    conn = get_connection()
    cursor = get_cursor(conn)
    path = os.path.join(os.getenv("download_directory"),
                        os.getenv("combined_csv_filename"))
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for line in reader:
            if line['val'] == os.getenv("request"):
                if line['type'] == os.getenv("assistance"):
                    cursor.execute("""INSERT INTO request_interaction
    (exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (line['site'], 1, line['at'],))
                elif line['type'] == os.getenv("emergency"):
                    cursor.execute("""INSERT INTO request_interaction
    (exhibition_id, request_id, event_at) VALUES (%s, %s, %s)""", (line['site'], 2, line['at'],))
            else:
                cursor.execute("""
                    INSERT INTO rating_interaction (exhibition_id, rating_id, event_at)
                    SELECT %s, rating_id, %s
                    FROM rating
                    WHERE rating_value = %s
                """, (line['site'], line['at'], line['val']))
            if row_limit and count >= row_limit:
                break
    conn.commit()
    logging.info(f"{count} rows uploaded to the database.")


def parse_arguments():
    """Parses arguments to the command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str,
                        help="AWS bucket name")
    parser.add_argument("--rows", type=int,
                        help="Number of rows to upload to the database")
    parser.add_argument("--log", type=str, choices=["file", "terminal"],
                        help="Number of rows to upload to the database")
    parser.add_argument("--helping", action="help",
                        help="Number of rows to upload to the database")
    return parser.parse_args()


def setup_logging(log_type: str):
    """Sets up logging configuration."""
    if log_type == "file":
        logging.basicConfig(filename='pipeline.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging(args.log)
    client = get_client()
    if args.bucket:
        bucket = args.bucket
    else:
        bucket = os.getenv("bucket_name")
    if check_bucket_exists(client, bucket):
        download_files(client, os.getenv("bucket_name"))
        logging.info('All files downloaded.')
        csv_files = combine_csv_files()
        print(csv_files)
        logging.info('All files combined.')
        delete_individual_csv_files(csv_files)
        logging.info('Original csv files deleted.')
        upload_data_to_database(args.rows)
        logging.info('All data uploaded to database.')
    else:
        logging.error(f"Bucket '{args.bucket}' not found.")
