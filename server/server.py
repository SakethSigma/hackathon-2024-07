from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from agents import *
import functools
from backend import perform_checks

app = Flask(__name__)
CORS(app)  # This will allow all origins by default

@app.route('/process_claim', methods=['POST'])
def process_claim():
    data = request.json

    result = perform_checks(data)
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
