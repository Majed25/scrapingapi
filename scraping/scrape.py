import os
import requests
from bs4 import BeautifulSoup
import time
import csv
import json
import re

# Strikers finishing
# 2023-2024 Big 5 European Leagues Defensive Action Stats
# For the other seasons:
# https://fbref.com/en/comps/Big5/2022-2023/shooting/2022-2023-Big-5-European-Leagues-Stats
# URls Collection for Shooting data
# transfer market data https://www.transfermarkt.com/premier-league/transfers/wettbewerb/GB1/plus/?saison_id=2023&s_w=&leihe=1&intern=0

# loading parameters
def load_params():
    import os
    file_path = os.path.join(os.path.dirname(__file__), 'parameters.json')
    with open(file_path, 'r') as f:
        params = json.load(f)
    return params

def generate_urls(base_url, url_template, cur_yr, szns_count):
    urls = [base_url]
    for i in range(szns_count):
        prvy = cur_yr - 1
        pprvy = cur_yr - 2
        cur_yr = prvy
        url = url_template.format(pprvy=pprvy, prvy=prvy)
        urls.append(url)
    return urls
def get_szn(cur_yr, url):
    pattern = re.search(r'/(\d{4}-\d{4})/', url)
    if pattern:
        season = pattern.group(1)[:4]
    else:
        season = cur_yr
    return season


def store_data(temp_dir, data_path, schema_path, table_header, extracted_data, schema):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    print(current_dir)
    parent_dir = os.path.dirname(current_dir)  # Navigate to the parent directory
    print(parent_dir)
    final_path = os.path.join(parent_dir, temp_dir)


    for path in [data_path, schema_path]:
        os.makedirs(final_path, exist_ok=True)


    path = os.path.join(final_path, data_path)

    with open(path, 'w', newline='') as csvfile:
        # Create a CSV writer
        csvwriter = csv.writer(csvfile)
        # Write the header
        print(len(table_header))
        csvwriter.writerow(table_header)
        # Write the data
        for row in extracted_data:
            if len(row) != len(table_header):
                print('lengths dont match len(row) len(header)', len(row), len(table_header))
                break
            else:
                csvwriter.writerow(row)

        # store schema
        path = os.path.join(final_path, schema_path)
        with open(path, 'w', newline='') as json_file:
            json.dump(schema, json_file, indent=2)


def get_shooting_data(params, szns_count=0):
    # leave seasons param as 0 to get only the current season
    base_url = params['url_params']['shooting_urls']['base']
    url_template = params['url_params']['shooting_urls']['urls']
    cur_yr = params['url_params']['year']

    # generate urls
    urls = generate_urls(base_url, url_template, cur_yr,szns_count)

    # extract the tables
    for url in urls:
        extracted_data = []
        response = requests.get(url)
        if response.status_code == 200:
            season = get_szn(cur_yr, url)
            soup = BeautifulSoup(response.content, 'html.parser')
            table_id = params['table_ids']['shooting']
            # Extract the  Header
            table = soup.find('table', {'id': table_id})
            # The header that contains the data column names
            t_header = table.find('thead').find_all('tr')[1]
            columns = t_header.find_all('th')
            columns_info = [column.get('aria-label', None) for column in columns]
            columns_info.append('season')
            table_header = [column.get_text(strip=True) for column in columns]
            table_header.append('season')
            # make a dictionary of data names and column info
            schema = {name: info for name, info in zip(table_header, columns_info)}
            print(f'scraping  {url}')

            # extract the table body
            table = soup.find('table', {'id': table_id})
            table_body = table.find('tbody')
            # exclude the header rows
            rows_to_exclude = table_body.find_all('tr', class_='thead rowSum')
            for row in rows_to_exclude:
                row.decompose()
            rows = table_body.find_all('tr')

            # get the data values from the first element being a th and the following being td
            for row in rows:
                data = []
                stats = row.find_all(['th', 'td'])
                for stat in stats:
                    # handling Na values
                    data.append('Na' if stat.text == '' else stat.text)
                data.append(season)
                extracted_data.append(data)

            # store data
            temp_dir = params['data_paths']['temp_data']
            data_path = params['data_paths']['temp_shoot_data'].format(season=season)
            schema_path = params['data_paths']['temp_shoot_schema'].format(season=season)
            store_data(temp_dir, data_path, schema_path, table_header, extracted_data, schema)
            time.sleep(5)
        else:
            print(f'Failed to retrieve the web page for URL: {url}')

def get_defensive_style(params, seasons=0):
    # leave seasons param as 0 to get only the current season
    base_url = params['url_params']['defensive_urls']['base']
    url_template = params['url_params']['defensive_urls']['urls']
    cur_yr = params['url_params']['year']

    urls = generate_urls(base_url, url_template, cur_yr, seasons)
    for url in urls:
        season = get_szn(cur_yr, url)
        response = requests.get(url)
        extracted_data = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table_id = params['table_ids']['defensive']
            # Extract the  Header
            table = soup.find('table', {'id': table_id})
            # The header that contains the data column names
            t_header = table.find('thead').find_all('tr')[1]
            columns = t_header.find_all('th')
            columns_info = [column.get('aria-label', None) for column in columns]
            columns_info.append('season')
            table_header = [column.get_text(strip=True) for column in columns]
            table_header.append('season')
            extracted_data.append(table_header)
            # make a dictionary of data names and column info
            schema = {name: info for name, info in zip(table_header, columns_info)}

            # extract the table body
            table_body = table.find('tbody')
            # exclude the header rows
            rows_to_exclude = table_body.find_all('tr', class_='thead rowSum')
            for row in rows_to_exclude:
                row.decompose()
            rows = table_body.find_all('tr')

            # get the data values from the first element being a th and the following being td
            for row in rows:
                data = []
                stats = row.find_all(['th', 'td'])
                for stat in stats:
                    # handling Na values
                    data.append('Na' if stat.text == '' else stat.text)
                data.append(season)
                extracted_data.append(data)

            # store the table in csv
            data_paths = params['data_paths']['temp_def_data'].format(season=season)
            schema_paths = params['data_paths']['temp_def_schema'].format(season=season)
            store_data(data_paths, schema_paths,table_header, extracted_data, schema)
            time.sleep(5)

        else:
            print(f'Error fetching table from {url}')

def get_op_passing(params, seasons=0):
    # leave seasons param as 0 to get only the current season
    base_url = params['url_params']['passing_urls']['opp_passing_urls']['base']
    url_template = params['url_params']['passing_urls']['opp_passing_urls']['urls']
    cur_yr = params['url_params']['year']
    urls = generate_urls(base_url, url_template, cur_yr, seasons)
    for url in urls:
        season = get_szn(cur_yr,  url)
        response = requests.get(url)
        extracted_data = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table_id = params['table_ids']['op_passing']
            # Extract the  Header
            table = soup.find('table', {'id': table_id})
            # The header that contains the data column names
            t_header = table.find('thead').find_all('tr')[1]
            columns = t_header.find_all('th')
            columns_info = [column.get('aria-label', None) for column in columns]
            columns_info.append(season)
            table_header = [column.get_text(strip=True) for column in columns]
            table_header.append(season)
            extracted_data.append(table_header)
            # make a dictionary of data names and column info
            schema = {name: info for name, info in zip(table_header, columns_info)}

            # extract the table body
            table_body = table.find('tbody')
            # exclude the header rows
            rows_to_exclude = table_body.find_all('tr', class_='thead rowSum')
            for row in rows_to_exclude:
                row.decompose()
            rows = table_body.find_all('tr')

            # get the data values from the first element being a th and the following being td
            for row in rows:
                data = []
                stats = row.find_all(['th', 'td'])
                for stat in stats:
                    # handling Na values
                    data.append('Na' if stat.text == '' else stat.text)
                data.append(season)
                extracted_data.append(data)

            # store the table in csv
            opp_pass_data_paths = params['data_paths']['temp_opp_data'].format(season=season)
            opp_pass_schema_paths = params['data_paths']['temp_opp_schema'].format(season=season)
            store_data(opp_pass_data_paths, opp_pass_schema_paths, table_header, extracted_data, schema)
            time.sleep(5)

        else:
            print(f'Error fetching table from {url}')





