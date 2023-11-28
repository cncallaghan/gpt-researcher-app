from flask import Flask, request, jsonify
# from config import Config
import json
import requests

app = Flask(__name__)
# config = Config()  # Instantiating the Config class
# stringify config

def is_valid_string(s):
    """Check if the input is a valid string."""
    return isinstance(s, str) and len(s.strip()) > 0

def capitalize_text(data):
    if isinstance(data, dict):
        return {k: capitalize_text(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [capitalize_text(item) for item in data]
    elif isinstance(data, str):
        return data.upper()
    else:
        return data
    

@app.route("/config", methods=["POST"])
def post_config():
    data = request.get_json()
    query = data.get("research_text")
    report_type = data.get("model")
    if not is_valid_string(query) or not is_valid_string(report_type):
        return jsonify({"error": "Invalid input"}), 400
    try:
        capitalized_data = capitalize_text(data)  # Capitalize text

        # Sending the modified data to another Lambda function
        outbound_url = "https://example.com/outbound-lambda"  # Replace with actual URL
        response = requests.post(outbound_url, json=capitalized_data)

        # return jsonify({"message": "Data received, processed, and sent successfully"}), 200
        return capitalized_data
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Error Handler
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

# Validate incoming configuration data
def validate_config_data(data):
    # Add validation logic here. For example, checking data types, ranges, etc.
    # Raise an exception if validation fails
    pass

# # Update Config dynamically
# def update_config_values(data):
#     for key, value in data.items():
#         if hasattr(config, key):
#             setattr(config, key, value)
#     # Optionally, save the updated configuration to a file

# @app.route("/config", methods=["POST"])
# def post_config():
#     data = request.get_json()
#     try:
#         validate_config_data(data)
#         update_config_values(data)
#         return jsonify({"message": "Configuration updated successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1')



