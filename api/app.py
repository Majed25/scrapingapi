from flask import Flask, jsonify
from scraping.merge_data import *
from scraping.scrape import *
from scraping.scrape_tfrs import *

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
    print(type(data_type), data_type)
    return jsonify({'data_type': data_type}), 200



if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5000)
    # Debug: Print parameters to verify the structure
    pass









