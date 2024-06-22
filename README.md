# Football Data Scraping API

This API provides endpoints to scrape and retrieve football data from various fbref.com and transfermarkt.com. It is built using Flask and designed to be easy to use and deploy.

## Usage

### Endpoints

- `/`: Returns a welcome message.
- `/api/data/<data_type>`: Returns football data based on the specified data type. Available data types are:
  - `shooting`: Shooting statistics
  - `defensive`: Defensive statistics
  - `op_pass`: Opposition passing statistics
  - `tfr`: Transfer data

### Request Example:

To get shooting statistics, you can make a GET request to `/api/data/shooting`:


### Legal Disclaimer

This API respects the website's robots.txt file and is intended for educational purposes only. Users of this API are responsible for complying with all relevant laws and regulations.


### API deploed and can be accessed here:
https://footballscrapingapi.azurewebsites.net/
