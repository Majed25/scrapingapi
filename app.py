import sys
from flask import Flask, jsonify
from scraping.merge_data import merge_data, clear_temp_data
from scraping.scrape import load_params, get_shooting_data, get_defensive_style, get_op_passing
from scraping.scrape_tfrs import scrape_transfers

app = Flask(__name__)
# Load parameters
params = load_params()

function_dict = {
    'shooting': get_shooting_data,
    'defensive': get_defensive_style,
    'op_pass': get_op_passing,
    'tfr': scrape_transfers
}

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!'}), 200

@app.route('/api/data/<data_type>', methods=['GET'])
def process_data(data_type):
    params = load_params()  # Load parameters
    function_dict[data_type](params)
    data = merge_data(data_type, params, return_data=True)
    return jsonify({'My Table ': data['data']}), 200




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # Debug: Print parameters to verify the structure









