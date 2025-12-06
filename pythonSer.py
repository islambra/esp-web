from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import socket
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===== GLOBAL =====
recording_thread = None
stop_event = threading.Event()

# ESP32 sends data to this socket
SERVER_HOST = "0.0.0.0"   # accept from any device
SERVER_PORT = 5010        # MUST MATCH ESP32 port


def recording_task(filename, label):
    global stop_event
    log_filename = f"{filename}.csv"
    stop_event.clear()

    print(f"[RECORDER] Waiting for ESP32 on port {SERVER_PORT}...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((SERVER_HOST, SERVER_PORT))
            server.listen(1)

            conn, addr = server.accept()
            print(f"[RECORDER] ESP32 connected from {addr}")

            with conn:
                with open(log_filename, mode="w", newline="") as file:
                    writer = csv.writer(file)

                    # ESP32 CSV header
                    writer.writerow([
                        "timestamp_pc",
                        "label",
                        "HAND_ID",
                        "esp_timestamp",
                        "ax", "ay", "az",
                        "gx", "gy", "gz"
                    ])

                    while not stop_event.is_set():
                        data = conn.recv(1024).decode().strip()
                        if not data:
                            break

                        # Example ESP line:
                        # RightHand,12345,0.12,-0.33,9.81,0.01,0.02,0.03
                        fields = data.split(",")

                        if len(fields) != 8:
                            print("[WARN] Invalid line:", data)
                            continue

                        writer.writerow([datetime.now().isoformat(), label] + fields)
                        print(f"[DATA] {fields}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        stop_event.clear()
        print("[RECORDER] Stopped.")


@app.route("/start", methods=["POST"])
def start_recording():
    global recording_thread

    if recording_thread and recording_thread.is_alive():
        return jsonify({"status": "error", "message": "Already recording."}), 400

    data = request.json
    filename = data.get("filename")
    label = data.get("label")

    if not filename:
        return jsonify({"status": "error", "message": "Filename required."}), 400

    recording_thread = threading.Thread(target=recording_task, args=(filename, label))
    recording_thread.start()

    return jsonify({"status": "success", "message": f"Recording started for {filename}"})


@app.route("/stop", methods=["POST"])
def stop_recording():
    global recording_thread, stop_event

    if not recording_thread or not recording_thread.is_alive():
        return jsonify({"status": "error", "message": "Not recording."}), 400

    stop_event.set()
    recording_thread.join(timeout=3)

    return jsonify({"status": "success", "message": "Recording stopped."})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
