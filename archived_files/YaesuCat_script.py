from flask import Flask, request, jsonify
import serial

app = Flask(__name__)

# Try to open COM21 safely
try:
    ser = serial.Serial("COM21", baudrate=38400, timeout=1)
    print("Opened COM21 successfully")
except Exception as e:
    print(f"Error opening COM21: {e}")
    ser = None

def send_cat(cmd: bytes):
    """Send CAT command and return response"""
    if ser is None:
        return b""
    ser.write(cmd)
    response = ser.read(64)  # adjust length if needed
    return response

@app.route("/get-frequency")
def get_frequency():
    """Query current frequency from rig"""
    ser.write(b"FA;")  # ASCII command to query frequency
    response = ser.read(64)
    return jsonify({
        "sent": "FA;",
        "response": response.decode("ascii", errors="ignore")
    })

@app.route("/set-frequency")
def set_frequency():
    """Set frequency in Hz (e.g. ?hz=7100000)"""
    hz = int(request.args.get("hz"))
    # Build ASCII CAT command: FA + 11-digit frequency + ;
    cmd_str = f"FA{hz:011d};"
    ser.write(cmd_str.encode("ascii"))
    response = ser.read(64)
    return jsonify({
        "sent": cmd_str,
        "response": response.decode("ascii", errors="ignore")
    })

@app.route("/")
def hello():
    return "Yaesu CAT Web Control Active"

if __name__ == "__main__":
    app.run(debug=True)
