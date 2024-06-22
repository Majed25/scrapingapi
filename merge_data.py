import glob
import pandas as pd
import os
import json
import shutil
import logging


def ensure_directories(paths):
    for path in paths:
        try:
            directory = os.path.dirname(path)
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logging.error(f'Error creating directory {directory}: {e}')


def write_data(params, csv_path, schema_path=None):
    # write data in csv
    file_paths = glob.glob(os.path.join('data/temp_data', '*.csv'))
    schema_paths = glob.glob(os.path.join('data/temp_data', '*.json'))

    data_frames = []
    schema = {}
    try:
        for file in file_paths:
            df = pd.read_csv(file)
            data_frames.append(df)
        concatenated_df = pd.concat(data_frames, ignore_index=True, sort=False)
        concatenated_df_json = concatenated_df.to_json()
    except Exception as e:
        logging.error(f'Error reading and concatenating CSV files: {e}')

    try:
        for path in schema_paths:
            with open(path, 'r') as file:
                current_schema = json.load(file)
            if len(current_schema) > len(schema):
                schema = current_schema
    except Exception as e:
        logging.error(f'Error reading JSON schema files: {e}')


    ensure_directories([csv_path, schema_path])
    concatenated_df.to_csv(csv_path, index=False)
    with open(schema_path, 'w', newline='') as json_file:
        json.dump(schema, json_file, indent=2)

    return {'data': concatenated_df_json, 'schema': schema}


def clear_temp_data(params):
    shutil.rmtree('data/temp_data')
    os.makedirs('data/temp_data', exist_ok=True)
    logging.info('Clearing Temp data')

def merge_data(data_type, params):
    data = params['data_paths'][data_type]['csv']
    schema = params['data_paths'][data_type]['schema']
    ensure_directories([data, schema])
    result = write_data(params, data, schema)
    clear_temp_data(params)
    logging.info('Merge and return data Success')
    return result

