#!/usr/bin/env python
# coding: utf-8

import os
import argparse

from time import time

import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user           = params.user
    password       = params.password
    host           = params.host
    port           = params.port
    db             = params.db
    table_name_1   = params.table_name_1
    table_name_2   = params.table_name_2
    url1           = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz'
    url2           = 'https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv'

    # bear that the data is in *.csv.gz
    csv1           = 'green_taxi.csv.gz'
    csv2           = 'zones_taxi.csv'

    print('checking if files are already downloaded:')
    # before downloading csv files
    csv1_exists    = os.path.exists(csv1)
    csv2_exists    = os.path.exists(csv2)

    if csv1_exists:
        print(f'{csv1} already exists')
    else:
        print('Downloading data for green taxi')
        os.system(f"wget {url1} -O {csv1}")
    if csv2_exists:
        print(f'{csv2} already exists')
    else:
        print('Downloading data for taxi zones')
        os.system(f"wget {url2} -O {csv2}")

    print("dowloads finished")

    # creating the connection to the db
    engine = create_engine(
        f'postgresql://{user}:{password}@{host}:{port}/{db}'
    )

    # engine.connect()

    # Green taxi trips data
    df_iter = pd.read_csv(csv1, iterator=True, chunksize=100000)
    df = next(df_iter)
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    print('Creating table for green taxi')

    df.head(n=0).to_sql(name=table_name_1, con=engine, if_exists='replace')

    df.to_sql(name=table_name_1, con=engine, if_exists='append')

    for chunk in df_iter:
        t_start = time()
        df = chunk
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        df.to_sql(name=table_name_1, con=engine, if_exists='append')

        t_end = time()
        print(f'inserted another chunk. Took {(t_end-t_start):.3f} seconds')
    
    print('finished green taxi data ingestion')
            
    print('Starting taxi zones data ingestion')
    # Taxi-zones data
    df = pd.read_csv(csv2)
    df.head(n=0).to_sql(name=table_name_2, con=engine, if_exists='replace')
    df.to_sql(name=table_name_2,con=engine,if_exists='append')

    print('data ingestion finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name_1', help='name of the table for trips')
    parser.add_argument('--table_name_2', help='name of the table for zones')
    #parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    main(args)