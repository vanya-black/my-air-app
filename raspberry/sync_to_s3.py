import os
from datetime import datetime, timedelta
import json
from numpy import diff
from fastavro import writer, reader, parse_schema
import boto3
import logging
from pathlib import Path
import sqlite3

DB_NAME = Path(Path.home(), 'air.db')
S3_HOST = os.environ.get('S3_HOST', 'https://storage.yandexcloud.net')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'None')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'None')
S3_BUCKET = os.environ.get('S3_BUCKET', 'air-data')

logging.basicConfig(filename=Path(Path.home(), 'sync.log'), encoding='utf-8', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

client = boto3.client(
    's3',
    endpoint_url = S3_HOST,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

with open(Path(Path.home(), 'my-air-app', 'air.avsc'), "rb") as f:
    schema = parse_schema(json.loads(f.read()))


def get_max_s3_timestamp() -> datetime:
    try:
        keys = client.list_objects(Bucket=S3_BUCKET)['Contents']
    except KeyError:
        return datetime(1970, 1, 1, 0)

    dates = []
    for key in keys:
        dates.append(datetime.strptime(key['Key'], '%Y/%m/%d/%H.avro'))
    return max(dates)


def convert_to_avro(data: list, name: str)->str:
    fname = f'{name}.avro'
    with open(fname, 'wb') as out:
        writer(out, schema, data)   
    return fname


max_ts = get_max_s3_timestamp()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

with sqlite3.connect(DB_NAME) as conn:
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute("""SELECT * FROM air_storage
                    WHERE dt > :max_dt """, {"max_dt": max_ts + timedelta(hours=1)})
    rows = cur.fetchall()

hours = sorted(list(set([datetime.fromisoformat(x['dt']).replace(minute=0, second=0, microsecond=0) for x in rows])))
hours.remove(datetime.utcnow().replace(minute=0, second=0, microsecond=0)) # delete curr hour
logging.info(f'max timestamp found in s3: {max_ts}')
logging.info(hours)
logging.info(f'Found {len(hours)} unsended hours')

for row in rows:
    row['dt'] = datetime.fromisoformat(row['dt'])

for hour in hours:
    data = [x for x in rows if x['dt'] > hour and x['dt'] < hour+timedelta(hours=1)]
    for d in data:
        del d['id']
    fname = convert_to_avro(data, str(hour.hour))
    client.upload_file(fname, S3_BUCKET, hour.strftime('%Y/%m/%d/%H.avro'))
    logging.info(f'Uploaded {len(data)} recors for {hour}')
    os.remove(fname)
