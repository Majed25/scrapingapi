from flask import Flask, jsonify
from scrape import *
from merge_data import *
from scrape_tfrs import *


function_dict = {
    'shooting': get_shooting_data,
    'defensive': get_defensive_style,
    'op_pass': get_op_passing,
    'tfr': scrape_transfers
}

params = load_params()

def main():
    scrape_transfers(params)
    merge_data('tfr',params)


if __name__ == '__main__':
    main()

