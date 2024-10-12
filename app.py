from flask import Flask, render_template, request, jsonify, abort, send_file, Response
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY')

file_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        file_id = str(uuid.uuid4())
        
        pinata_response = upload_to_pinata(file)

        if pinata_response.status_code != 200:
            return jsonify({"message": "Error uploading file to Pinata", "error": pinata_response.json()}), 500

        pinata_hash = pinata_response.json()['IpfsHash']
        file_store[file_id] = {
            "file_hash": pinata_hash,
            "file_name": file.filename
        }

        share_url = request.host_url + f'file/{file_id}'
        download_url = request.host_url + f'file/{file_id}/download'
        return jsonify({"message": "File uploaded", "url": share_url, "download_url": download_url, "file_name": file.filename})
    except Exception as e:
        return jsonify({"message": "File upload failed", "error": str(e)}), 500

def upload_to_pinata(file):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }
    files = {'file': file.stream}
    return requests.post(url, files=files, headers=headers)

@app.route('/file/<file_id>', methods=['GET'])
def view_file(file_id):
    file_data = file_store.get(file_id)

    if not file_data:
        return abort(404, description="File not found")

    pinata_url = f"https://gateway.pinata.cloud/ipfs/{file_data['file_hash']}"
    response = requests.get(pinata_url, stream=True)
    
    if response.status_code != 200:
        return abort(404, description="File not found on IPFS")

    # Return inline view in browser
    return Response(response.content, mimetype='application/octet-stream')

@app.route('/file/<file_id>/download', methods=['GET'])
def download_file(file_id):
    file_data = file_store.get(file_id)

    if not file_data:
        return abort(404, description="File not found")

    pinata_url = f"https://gateway.pinata.cloud/ipfs/{file_data['file_hash']}"
    response = requests.get(pinata_url, stream=True)
    
    if response.status_code != 200:
        return abort(404, description="File not found on IPFS")

    # Return file as attachment to be downloaded
    return send_file(
        response.raw,
        as_attachment=True,
        download_name=file_data['file_name'],
        mimetype='application/octet-stream'
    )

@app.route('/files', methods=['GET'])
def list_files():
    return jsonify(file_store)

if __name__ == '__main__':
    app.run(debug=True)
