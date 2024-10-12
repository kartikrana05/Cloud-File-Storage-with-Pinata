import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv  # Import dotenv for environment variables

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load API keys from environment variables
PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_API_SECRET = os.getenv('PINATA_API_SECRET')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Use Pinata's API to upload the file
    response = requests.post(
        'https://api.pinata.cloud/pinning/pinFileToIPFS',
        files={'file': file},
        headers={
            'pinata_api_key': PINATA_API_KEY,
            'pinata_secret_api_key': PINATA_API_SECRET
        }
    )

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': response.json()}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
