import requests
import time
import json
import os

# Endpoint for gyroscope data
GYRO_ENDPOINT = "http://3.145.161.54:5000/gyro"

# Path to save the transformation JSON
TRANSFORM_JSON_PATH = "scripts/transform.json"

def fetch_gyro_data():
    """
    Fetch gyroscope data from the external endpoint and parse it.
    """
    try:
        response = requests.get(GYRO_ENDPOINT, timeout=5)  # Add timeout to avoid hanging
        response.raise_for_status()
        data = response.json()

        # Extract the 'last_entry' key from the JSON
        last_entry = data.get("last_entry", {})
        if not last_entry:
            print("No 'last_entry' found in the response.")
            return None

        # Parse rotation and position
        rotation = [
            float(last_entry.get("rotationX", 0.0)),
            float(last_entry.get("rotationY", 0.0)),
            float(last_entry.get("rotationZ", 0.0)),
        ]
        position = [
            float(last_entry.get("positionX", 0.0)),
            float(last_entry.get("positionY", 0.0)),
            float(last_entry.get("positionZ", 0.0)),
        ]

        return rotation, position
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching gyroscope data: {e}")
        return None, None

def save_to_json(rotation, position):
    """
    Save the transformation data to a JSON file.
    """
    transform_data = {
        "rotation": rotation,
        "position": position
    }

    try:
        with open(TRANSFORM_JSON_PATH, "w") as json_file:
            json.dump(transform_data, json_file, indent=4)
        print(f"Saved transformation data to {TRANSFORM_JSON_PATH}")
    except IOError as e:
        print(f"Error saving to JSON file: {e}")

def main():
    interval = 0.1  # Time interval in seconds
    while True:
        rotation, position = fetch_gyro_data()
        if rotation and position:
            print(f"Rotation: {rotation}, Position: {position}")
            save_to_json(rotation, position)
        else:
            print("Failed to fetch gyroscope data or invalid format.")

        time.sleep(interval)  # Wait for the specified interval before fetching again

if __name__ == "__main__":
    main()
