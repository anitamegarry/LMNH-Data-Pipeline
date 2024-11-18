"""
Extracts relevant museum data from AWS S3 and combines all csv data
"""

import boto3
import os

from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()


def get_client() -> boto3.client:
    """Returns S3 client"""
    access_key_id = os.getenv("access_key_ID")
    secret_access_key = os.getenv("secret_access_key")
    client = boto3.client(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )
    return client


def list_s3_buckets(client: boto3.client) -> None:
    """Lists available buckets within the S3"""
    response = client.list_buckets()
    print("S3 Buckets:")
    for bucket in response['Buckets']:
        print(f" - {bucket['Name']}")


def check_bucket_exists(client: boto3.client, args=os.getenv("bucket_name")):
    """Returns bucket name if bucket exists"""
    try:
        bucket_name = args
        client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' exists.")
        return bucket_name
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code:
            print(f"Bucket '{bucket_name}' does not exist.")
        return None


def download_files(client: boto3.client, bucket_name, download_directory='downloads'):
    """Downloads lmnh museum files from a bucket"""
    if not os.path.exists(download_directory):
        os.makedirs(download_directory, exist_ok=True)

    try:
        response = client.list_objects_v2(Bucket=bucket_name)

        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key']

                if file_name.startswith('lmnh'.lower()) and (
                        file_name.endswith('.json') or file_name.endswith('.csv')):
                    print(f"Downloading: {file_name}")
                    file_path = os.path.join(download_directory, file_name)

                    client.download_file(bucket_name, file_name, file_path)
                else:
                    print(f"Skipping: {file_name} (does not contain 'lmnh')")
        else:
            print(f"No files found in the bucket '{bucket_name}'.")

    except ClientError as e:
        print(
            f"Error while listing/downloading files from '{bucket_name}': {e}")


def combine_csv_files() -> list[str]:
    """Combines csv files together"""
    download_dir = os.getenv("download_directory")
    filename = os.getenv("combined_csv_filename")
    combined_file_path = os.path.join(download_dir, filename)

    print(f"Combining CSV files in directory: {download_dir}")

    with open(combined_file_path, 'w', newline='') as combined_file:
        combined_file.write("at,site,val,type\n")
        combined_file.flush()
        csv_files = [
            f for f in os.listdir(download_dir) if f.startswith(os.getenv("start_of_file")
                                                                ) and f.endswith('.csv') and f != filename]
        if not csv_files:
            print("No CSV files found to combine.")
            return []
        print(f"CSV files to combine: {csv_files}")
        for filename in csv_files:
            file_path = os.path.join(download_dir, filename)
            print(f"Processing file: {file_path}")

            with open(file_path, 'r') as open_csv:
                first_row = True
                for line in open_csv:
                    if first_row:
                        first_row = False
                        continue
                    combined_file.write(line)
                    combined_file.flush()
    print(f"Combined CSV files have been saved to {combined_file_path}")
    return [os.path.join(download_dir, f) for f in csv_files]


def delete_individual_csv_files(csv_files) -> None:
    """Deletes original csv files"""
    for file_path in csv_files:
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")


if __name__ == "__main__":
    client = get_client()
    check_bucket_exists(client)
    download_files(client, os.getenv("bucket_name"))
    csv_files = combine_csv_files()
    delete_individual_csv_files(csv_files)
