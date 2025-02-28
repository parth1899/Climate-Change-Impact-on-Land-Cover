from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from backend.map_helper.o3_map_generator import ozone_main

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

CORS(app)

@app.route('/api/generate_maps', methods=['POST'])
def generate_maps():
    #get the request data
    data = request.json

    dataset = data.get('dataset')
    start_year = data.get('start_year')
    end_year = data.get('end_year')
    selected_regions = data.get('selected_regions')

    try:
        print(f"Generating maps for {dataset} from {start_year} to {end_year} for regions: {selected_regions}")

        #generate the maps
        #if-else statements based on datasets
        if dataset == 'Ozone':
            urls, stats, legends, geojson_data, selected_regions = ozone_main(selected_regions, start_year, end_year)

        return jsonify({
            'urls': urls,
            'legends': legends,
            'geojson_data': geojson_data,
            'selected_regions': selected_regions,
            'stats': stats
        })
    
    except Exception as e:
        print(f"Error generating maps: {str(e)}")
        return jsonify({
            'error': str(e)
        })


@app.route('/')
def index():
    """Render the main page for the visualization."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)