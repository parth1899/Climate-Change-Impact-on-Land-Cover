from flask import Flask, request, jsonify
from services.gpr_service import fetch_data_service  # Import the service function

app = Flask(__name__)

@app.route("/fetch_data", methods=["POST"])
def fetch_data():
    try:
        data = request.json  # Get JSON payload from the client
        result = fetch_data_service(data)  # Delegate processing to gpr_service
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
