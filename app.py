from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from backend.map_helper.map_generator import generate_no2_maps
from backend.data_processors.no2_data_processor import NO2DataProcessor

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

CORS(app)

@app.route('/generate_maps', methods=['POST'])
def generate_maps():
    data = request.json
    selected_years = data.get('selected_years', [])
    selected_classes = data.get('selected_classes', [])
    region_name = data.get('region_name', '')
    geojson_path = 'boundaries/datasets/maharashtra_districts.geojson'

    data_processor = NO2DataProcessor({
        'years': selected_years,
        'region': region_name,
        'levels': selected_classes
        })

    df = data_processor.process_data()

    print(df)
    
    return "Success"
    # try:
    #     result = generate_no2_maps(
    #         selected_years=selected_years, 
    #         selected_classes=selected_classes,
    #         region_name=region_name,
    #         geojson_path=geojson_path
    #     )
    #     return jsonify(result)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Render the main page for the visualization."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)