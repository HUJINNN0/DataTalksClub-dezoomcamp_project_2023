from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from random import randint
from prefect.tasks import task_input_hash
from datetime import timedelta


@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""
    # if randint(0, 1) > 0:
    #     raise Exception

    df = pd.read_csv(dataset_url)
    return df


@task(log_prints=True)
def clean(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Fix dtype issues"""
    if color == "yellow":
        df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
        df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    if color == "green":
        df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
        df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
    if color == "fhv":
        df.rename({'dropoff_datetime': 'dropOff_datetime'}, axis='columns', inplace=True)
        df["dropOff_datetime"] = pd.to_datetime(df["dropOff_datetime"])
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df.astype({
                # green tripdata:
        ##'VendorID': 'Int64',
        ##'store_and_fwd_flag': 'string',
        ##'passenger_count': 'Int64',
        ##'trip_distance': 'float64',
        ##'PULocationID': 'Int64',
        ##'DOLocationID': 'Int64',
        ##'RatecodeID': 'Int64',
        ##'payment_type': 'Int64',
        ##'fare_amount': 'float64',
        ##'extra': 'float64',
        ##'mta_tax': 'float64',
        ##'improvement_surcharge': 'float64',
        ##'tip_amount': 'float64',
        ##'tolls_amount': 'float64',
        ##'total_amount': 'float64',
        ##'congestion_surcharge': 'float64',
        ##'ehail_fee': 'float64',
        ##'trip_type': 'Int64',
                # yellow tripdata:
        ##'VendorID': 'Int64',
        ##'passenger_count': 'Int64',
        ##'trip_distance': 'float64',
        ##'PULocationID': 'Int64',
        ##'DOLocationID': 'Int64',
        ##'RatecodeID': 'Int64',
        ##'store_and_fwd_flag': 'string',
        ##'payment_type': 'Int64',
        ##'fare_amount': 'float64',
        ##'extra': 'float64',
        ##'mta_tax': 'float64',
        ##'improvement_surcharge': 'float64',
        ##'tip_amount': 'float64',
        ##'tolls_amount': 'float64',
        ##'total_amount': 'float64',
        ##'congestion_surcharge': 'float64',
                # fhv 2019:
        'dispatching_base_num': 'string',
        'PUlocationID': 'Int64',
        'DOlocationID': 'Int64',
        'SR_Flag': 'Int64',
        'Affiliated_base_number': 'str'
    })


@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    path = Path(f"{dataset_file}.csv.gz")
    df.to_parquet(path, compression="gzip")
    return path


@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return


@flow()
def etl_web_to_gcs(year: int, month: int, color: str) -> None:
    """The main ETL function"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(
        df, color
    )
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)


@flow()
def etl_parent_flow(
    months: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], year: int = 2019, color: str = "fhv"
):
    for month in months:
        etl_web_to_gcs(year, month, color)


if __name__ == "__main__":
    color = "fhv"
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    year = 2019
    etl_parent_flow(months, year, color)
