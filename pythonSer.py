from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import socket
import csv
from datetime import datetime
import time
import random

app = Flask(__name__)
CORS(app)

# ===== Global State =====
recording_thread = None
stop_event = threading.Event()
recording_label = ""

# ===== Server Configuration =====
# This is the address of the device sending data (e.g., ESP32)
# You might need to change this to the correct IP and Port.
DATA_SOURCE_HOST = "127.0.0.1"  # This should be the IP of your ESP32 or data source
DATA_SOURCE_PORT = 8080         # The port your data source is sending data on

# This is the configuration for this web server
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

def recording_task(filename, label):
    """
    This function runs in a background thread.
    It opens a socket to listen for data, and writes it to a CSV file.
    """
    global stop_event
    log_filename = f"{filename}.csv"

    print(f"[RECORDER] Starting recording to {log_filename} with label '{label}'")

    try:
        # Instead of a real socket, we will generate dummy data for now.
        # This simulates receiving data from a device like an ESP32.
        # To switch to a real socket, replace the while loop with the commented-out
        # socket code below.

        with open(log_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "label", "value1", "value2", "value3"])

            while not stop_event.is_set():
                # Generate dummy data
                timestamp = datetime.now().isoformat()
                value1 = random.randint(0, 100)
                value2 = random.randint(0, 100)
                value3 = random.randint(0, 100)
                
                writer.writerow([timestamp, label, value1, value2, value3])
                print(f"[DATA] {timestamp}, {label}, {value1}, {value2}, {value3}")
                
                # Simulate receiving data every second
                time.sleep(1)

        # =====================================================================
        # REAL SOCKET CODE (for when you have a device sending data)
        # =====================================================================
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.bind((DATA_SOURCE_HOST, DATA_SOURCE_PORT))
        #     s.listen()
        #     print(f"[RECORDER] Waiting for data source on {DATA_SOURCE_HOST}:{DATA_SOURCE_PORT}...")
        #     conn, addr = s.accept()
        #     with conn:
        #         print(f"[RECORDER] Connected by {addr}")
        #         with open(log_filename, mode="w", newline="") as file:
        #             writer = csv.writer(file)
        #             writer.writerow(["timestamp", "label", "field1", "field2", "field3", ...]) # Customize headers
        #             while not stop_event.is_set():
        #                 data = conn.recv(1024).decode('utf-8')
        #                 if not data:
        #                     break
        #                 # Assuming data is comma-separated, like "val1,val2,val3"
        #                 row_data = data.strip().split(',')
        #                 writer.writerow([datetime.now().isoformat(), label] + row_data)
        # =====================================================================

    except Exception as e:
        print(f"[RECORDER-ERROR] {e}")
    finally:
        print(f"[RECORDER] Stopping recording for {log_filename}.")
        stop_event.clear()


@app.route('/start', methods=['POST'])
def start_recording():
    global recording_thread, stop_event, recording_label

    if recording_thread and recording_thread.is_alive():
        return jsonify({"status": "error", "message": "Already recording."}), 400

    data = request.json
    filename = data.get('filename')
    label = data.get('label')

    if not filename:
        return jsonify({"status": "error", "message": "Filename is required."}), 400
    
    stop_event.clear()
    recording_label = label
    recording_thread = threading.Thread(target=recording_task, args=(filename, label))
    recording_thread.start()

    return jsonify({"status": "success", "message": f"Started recording to {filename}.csv with label {label}."})


@app.route('/stop', methods=['POST'])
def stop_recording():
    global recording_thread, stop_event

    if not recording_thread or not recording_thread.is_alive():
        return jsonify({"status": "error", "message": "Not currently recording."}), 400

    stop_event.set()
    recording_thread.join(timeout=5) # Wait for the thread to finish

    if recording_thread.is_alive():
         return jsonify({"status": "error", "message": "Could not stop the recording thread."}), 500

    recording_thread = None
    return jsonify({"status": "success", "message": "Stopped recording."})


if __name__ == '__main__':
    # Note: Using debug=False is important for this to work correctly with threads
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
