from bs4 import BeautifulSoup
import requests
import time
import csv
import re
import json
import random
import sys
import os
import logging


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
    logging.info(f'Generated transfer URLs: {urls}')
    return urls


def scrape_transfers(params, start_yr=None):
    try:
        # Scrape Each URL
        req_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
        }

        urls = generate_tfr_urls(params, start_yr)
        logging.info(f'Starting transfer data scraping for URLs: {urls}')
        for url in urls:
            html_content = requests.get(url,headers=req_headers)
            season = re.findall(r'\d{4}', url)[0]
            league = re.findall(r'\.com/([^/]+)/transfers', url)[0]
            logging.debug(f'season, league:{season}, {league}')
            if html_content.status_code == 200:
                logging.info(f'Successfully retrieved data for URL: {url}')
                soup = BeautifulSoup(html_content.text, 'html.parser')
                team_tags_html = soup.find_all('h2', class_="content-box-headline content-box-headline--inverted content-box-headline--logo")
                team_names = []
                for team_tag in team_tags_html:
                    team_name = team_tag.find_all('a')[1]
                    if team_name:
                        team_names.append(team_name.text.strip())
                logging.debug(f'Extracted team names: {team_names}')

                # getting the tables
                tables = soup.find_all('div', class_='responsive-table')
                tables = tables[::2]
                soup = BeautifulSoup(str(tables), 'html.parser')
                target_tables = soup.find_all('table')
                # open csv file
                csv_file_path = f'data/temp_data/{league}_{season}_team_transfer.csv'
                logging.info(f'Storing transfer data at: {csv_file_path}')


                with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
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
                    logging.debug(f'CSV headers written: {my_headers}')


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
                    logging.info(f'Successfully written data for team: {team} and season: {season}')


            else:
                logging.error(f'Failed to retrieve data for URL: {url}, Status Code: {html_content.status_code}')

        time.sleep(5)

    except Exception as e:
        logging.error(f'Error in get_op_passing:{e}')

           




