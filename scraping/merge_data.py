import glob
import pandas as pd
import os
import json
import shutil


def ensure_directories(paths):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for path in paths:
        full_path = os.path.join(base_path, path)
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)


def write_data(params, csv_path, schema_path=None, return_data=False):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    temp_data_path = params["data_paths"]["temp_data"]
    parent_dir = os.path.join(base_path, temp_data_path)

    file_paths = glob.glob(os.path.join(parent_dir, '*.csv'))
    schema_paths = glob.glob(os.path.join(parent_dir, '*.json'))

    data_frames = []
    schema = {}
    for file in file_paths:
        df = pd.read_csv(file)
        data_frames.append(df)
    concatenated_df = pd.concat(data_frames, ignore_index=True, sort=False)
    concatenated_df_json = concatenated_df.to_json()
    for path in schema_paths:
        with open(path, 'r') as file:
            current_schema = json.load(file)
        if len(current_schema) > len(schema):
            schema = current_schema

    if return_data:
        return {'data': concatenated_df_json, 'schema': schema}

    ensure_directories([csv_path, schema_path])
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('base path', base_path)
    csv_path = os.path.join(base_path, csv_path)
    print('csv path', csv_path)
    concatenated_df.to_csv(csv_path, index=False)
    schema_path = os.path.join(base_path, schema_path)

    with open(schema_path, 'w', newline='') as json_file:
        json.dump(schema, json_file, indent=2)


def clear_temp_data(params):
    temp_data_path = f'{params["data_paths"]["temp_data"]}'
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    path = os.path.join(base_path, temp_data_path)
    shutil.rmtree(path)
    os.makedirs(path)

def merge_data(data_type, params, return_data=False):
    data = params['data_paths'][data_type]['csv']
    schema = params['data_paths'][data_type]['schema']
    ensure_directories([data, schema])
    result = write_data(params, data, schema, return_data)
    clear_temp_data(params)
    if return_data:
        return result

