from flask import Flask, jsonify
from merge_data import merge_data
from scrape import load_params, get_shooting_data, get_defensive_style, get_op_passing
from scrape_tfrs import scrape_transfers
from flask_caching import Cache
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Set up app
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Load parameters
params = load_params()

function_dict = {
    'shooting': get_shooting_data,
    'defensive': get_defensive_style,
    'op_pass': get_op_passing,
    'tfr': scrape_transfers
}

@app.route('/')
@cache.cached(timeout=60)
def home():
    app.logger.info("Cache Missed: serving from file")
    return jsonify({'message': 'Welcome to the Flask API!'}), 200

@app.route('/api/data/<data_type>', methods=['GET'])
@cache.cached(timeout=60)
def process_data(data_type):
    app.logger.info("No cache")
    params = load_params()  # Load parameters
    function_dict[data_type](params)
    data = merge_data(data_type, params)
    return jsonify({'data_table': data['data']}), 200

if __name__ == '__main__':
    logging.info('Starting the Application')
    app.run(debug=False, host='0.0.0.0', port=5000)
    # Debug: Print parameters to verify the structure





