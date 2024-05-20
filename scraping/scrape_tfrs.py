from bs4 import BeautifulSoup
import requests
import time
import csv
import re
import json
import random
import sys
import os


def generate_tfr_urls(params, start_yr):
    if start_yr == None:
        start_yr = params['url_params']['year'] - 1
    end_yr = params['transfers']['seasons_range']['end_yr']
    seasons = [yr for yr in range(start_yr, end_yr)]
    leagues = params['transfers']['leagues']
    urls = []
    for league, lg in leagues.items():
        for season in seasons:
            url = params['url_params']['transfers_urls'].format(league=league, lg=lg, season=season)
            urls.append(url)
    return urls


def scrape_transfers(params, start_yr=None):
    # Scrape Each URL
    req_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
    }

    urls = generate_tfr_urls(params, start_yr)
    print(urls)
    for url in urls[:1]:
        print(f'scraping {url}')
        html_content = requests.get(url,headers=req_headers)
        season = re.findall(r'\d{4}', url)[0]
        league = re.findall(r'\.com/([^/]+)/transfers', url)[0]
        if html_content.status_code == 200:
            print('Success')
            soup = BeautifulSoup(html_content.text, 'html.parser')
            team_tags_html = soup.find_all('h2', class_="content-box-headline content-box-headline--inverted content-box-headline--logo")
            team_names = []
            for team_tag in team_tags_html:
                team_name = team_tag.find_all('a')[1]
                if team_name:
                    team_names.append(team_name.text.strip())

            # getting the tables
            tables = soup.find_all('div', class_='responsive-table')
            tables = tables[::2]
            soup = BeautifulSoup(str(tables), 'html.parser')
            target_tables = soup.find_all('table')
            # open csv file
            csv_file_path = f'{params['data_paths']['temp_data']}/{league}_{season}_team_transfer.csv'
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            path = os.path.join(base_path, csv_file_path)

            with open(path, 'w', newline='', encoding='utf-8') as csv_file:
                # Create a CSV writer object
                csv_writer = csv.writer(csv_file)
                # write the table header
                headers = [col.text.strip() for col in target_tables[0].find('thead').find('tr').find_all('th')]

                # I need to dublicate the column in my header because it contains 2 elements.
                LEFT_index = headers.index('Left')
                my_headers = headers[:LEFT_index + 1]
                my_headers.append('previous_team')
                my_headers = my_headers + headers[LEFT_index+1:]
                my_headers.append('current_team')
                my_headers.append('season')
                csv_writer.writerow(my_headers)

                # parse the table data
                for table, team in zip(target_tables, team_names):

                    # get the tr tags "rows"
                    rows_tags = [tr for tr in table.find('tbody').find_all('tr')]
                    for tr in rows_tags:
                        soup = BeautifulSoup(str(tr), 'html.parser')
                        data = [dt.text.strip() if dt.text else 'Nan' for dt in soup.find_all('td')]
                        data.append(team)
                        data.append(season)
                        csv_writer.writerow(data)

        else:
            print(html_content.status_code)

        time.sleep(5)




