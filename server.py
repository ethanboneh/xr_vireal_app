from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import CORS
import csv
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directories and file paths
UPLOAD_FOLDER = 'uploads'
GYRO_FILE = 'gyro.csv'
RENDER_FILE = 'render.png'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure required directories and files exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def ensure_gyro_file_exists():
    """Ensure the gyro.csv file exists and has a header if created."""
    if not os.path.exists(GYRO_FILE):
        with open(GYRO_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['positionX', 'positionY', 'positionZ', 'rotationX', 'rotationY', 'rotationZ'])
        print("Created gyro.csv with headers.")

ensure_gyro_file_exists()

@app.route('/')
def index():
    """Home route to confirm the server is running."""
    return "Unified server is running."

# Image upload and listing functionalities
@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint to upload a file to the uploads folder."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        timestamp = int(time.time())
        filename = secure_filename(f"{timestamp}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": f"File {filename} uploaded successfully!"}), 200

@app.route('/upload', methods=['GET'])
def list_and_delete_files():
    """Return all images from the uploads folder and then delete them."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if not files:
        return jsonify({"message": "No files found in the uploads folder."}), 200

    file_list = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in files]
    for file_path in file_list:
        os.remove(file_path)

    return jsonify({"files": files, "message": "All files listed and deleted from uploads folder."}), 200

# Gyro data functionalities for position and rotation
@app.route('/gyro', methods=['POST'])
def receive_gyro_data():
    """Endpoint to receive position and rotation data from Unity and store them in gyro.csv."""
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ['positionX', 'positionY', 'positionZ', 'rotationX', 'rotationY', 'rotationZ']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Invalid data format. Expected position and rotation fields."}), 400

    # Append the data to the CSV file
    with open(GYRO_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data['positionX'], data['positionY'], data['positionZ'], data['rotationX'], data['rotationY'], data['rotationZ']])
        print(f"Data {data} saved to {GYRO_FILE}.")

    return jsonify({"message": "Gyro data received and stored successfully!"}), 200

@app.route('/gyro', methods=['GET'])
def get_last_gyro_data():
    """Endpoint to retrieve the last entry of position and rotation data from gyro.csv."""
    try:
        with open(GYRO_FILE, mode='r') as file:
            reader = csv.reader(file)
            last_row = None
            for row in reader:
                last_row = row
            # Return the last data entry (ignoring the header if present)
            if last_row:
                return jsonify({"last_entry": {
                    "positionX": last_row[0],
                    "positionY": last_row[1],
                    "positionZ": last_row[2],
                    "rotationX": last_row[3],
                    "rotationY": last_row[4],
                    "rotationZ": last_row[5]
                }}), 200
            else:
                return jsonify({"error": "No data available"}), 404
    except Exception as e:
        print(f"Error reading {GYRO_FILE}: {e}")
        return jsonify({"error": "Could not retrieve data"}), 500

@app.route('/gyro/all', methods=['GET'])
def get_all_gyro_data():
    """Endpoint to retrieve all entries of position and rotation data from gyro.csv."""
    try:
        data = []
        with open(GYRO_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                data.append({
                    "positionX": row[0],
                    "positionY": row[1],
                    "positionZ": row[2],
                    "rotationX": row[3],
                    "rotationY": row[4],
                    "rotationZ": row[5]
                })
        
        if data:
            return jsonify({"all_entries": data}), 200
        else:
            return jsonify({"message": "No data available"}), 404
    except Exception as e:
        print(f"Error reading {GYRO_FILE}: {e}")
        return jsonify({"error": "Could not retrieve data"}), 500

# VR image handling functionalities
@app.route('/vrside', methods=['POST'])
def save_render_image():
    """Endpoint to receive an image and save it as render.png, overwriting the previous one."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file:
        file.save(RENDER_FILE)
        print(f"Image saved as {RENDER_FILE}.")
        return jsonify({"message": "Image uploaded and saved as render.png"}), 200

@app.route('/vrside', methods=['GET'])
def get_render_image():
    """Endpoint to retrieve the render.png image."""
    if os.path.exists(RENDER_FILE):
        return send_file(RENDER_FILE, mimetype='image/png')
    else:
        return jsonify({"error": "No image available"}), 404


# In-memory storage for integers (optional, depending on your use case)
received_integers = []

@app.route('/int_channel', methods=['POST'])
def receive_single_integer():
    """Endpoint to receive and process a single integer."""
    try:
        # Extract the integer from the JSON payload
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Invalid input. Expected JSON with a 'value' key."}), 400
        
        # Ensure it's an integer
        value = data['value']
        if not isinstance(value, int):
            return jsonify({"error": "Invalid input. 'value' must be an integer."}), 400
        
        # Add the integer to in-memory storage (or process it as needed)
        received_integers.append(value)
        print(f"Received integer: {value}")

        return jsonify({"message": "Integer received successfully!", "value": value}), 200
    except Exception as e:
        print(f"Error processing input: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

@app.route('/int_channel', methods=['GET'])
def get_received_integers():
    """Endpoint to retrieve all received integers."""
    if not received_integers:
        return jsonify({"message": "No integers received yet."}), 200
    
    return jsonify({"received_integers": received_integers}), 200


@app.route('/analytics', methods=['POST'])
def handle_analytics():
    # Handle both FormData and JSON
    if request.content_type.startswith('multipart/form-data'):
        scene_id = request.form.get('scene_id')
        timestamp = request.form.get('timestamp')
    else:
        data = request.get_json()
        scene_id = data.get('scene_id')
        timestamp = data.get('timestamp')
    return jsonify({'status': 'success', 'message': 'Analytics recorded', 'id': str(scene_id)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
