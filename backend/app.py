from flask import Flask, jsonify
from flask_cors import CORS
from climate_data_processing import load_climate_data, calculate_correlation
import traceback

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Route to fetch climate data and its correlation matrix
@app.route('/api/data', methods=['GET'])
def get_climate_data():
    try:
        # Load and process the climate data from CSVs
        data = load_climate_data('data/Annual_Surface_Temperature_Change.csv', 
                                 'data/Land_Ocean_Temperature_Index.csv')

        # Calculate correlation matrix
        correlation_matrix = calculate_correlation(data)

        # Return the climate data along with latitude and longitude to the frontend
        return jsonify({
            'data': data.to_dict(orient='records'),  # Convert the dataframe to a list of dictionaries
            'correlation': correlation_matrix
        }), 200

    except Exception as e:
        # Print the full traceback for debugging
        print("Error occurred: ", str(e))
        traceback.print_exc()  # This will print the stack trace to the console
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
