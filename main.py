from typing import Optional
from flask import Flask, render_template_string, jsonify, Response, stream_with_context
import serial
import threading
import time
import json

app = Flask(__name__)

SER_PORT = "COM21"
SER_BAUD = 38400

ser: Optional[serial.Serial] = None
latest_freq = "Unknown"
latest_freq_b = "Unknown"
latest_lock = threading.Lock()
latest_lock_b = threading.Lock()


def open_serial() -> None:
    global ser
    backoff = 1.0
    while True:
        try:
            ser = serial.Serial(
                port=SER_PORT,
                baudrate=SER_BAUD,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,
                # shorter timeout so reads return quickly and the UI updates faster
                timeout=0.2,
            )
            return
        except (serial.SerialException, OSError):
            ser = None
            time.sleep(backoff)
            backoff = min(10.0, backoff * 2)


def parse_frequency(raw: str) -> str:
    if (raw.startswith("FA") or raw.startswith("FB")) and raw.endswith(";"):
        hz_str = raw[2:-1]
        try:
            hz = int(hz_str)
            mhz = hz / 1_000_000
            return f"{mhz:.5f} MHz"
        except ValueError:
            return "Invalid frequency"
    return raw


def poll_frequency() -> None:
    global ser, latest_freq, latest_freq_b
    while True:
        try:
            # ensure we have a serial instance open
            if ser is None or not getattr(ser, "is_open", False):
                open_serial()

            # Use a local variable so type-checkers/IDEs don't think it may be None
            s = ser
            if s is None:
                # no serial yet; wait a short time and retry
                time.sleep(0.05)
                continue

            # reset/flush input buffer if available; be defensive about APIs
            try:
                s.reset_input_buffer()
            except AttributeError:
                try:
                    s.flushInput()
                except Exception:
                    pass

            # Query frequency A
            s.write(b"FA;")
            response = s.readline().decode(errors="ignore").strip()
            if response:
                parsed = parse_frequency(response)
                with latest_lock:
                    latest_freq = parsed

            # Query frequency B
            s.write(b"FB;")
            response_b = s.readline().decode(errors="ignore").strip()
            if response_b:
                parsed_b = parse_frequency(response_b)
                with latest_lock_b:
                    latest_freq_b = parsed_b

        except (serial.SerialException, OSError) as e:
            with latest_lock:
                latest_freq = f"Error: {e}"
            with latest_lock_b:
                latest_freq_b = f"Error: {e}"
            try:
                if ser is not None:
                    ser.close()
            except Exception:
                pass
            ser = None
            # back off a little longer on error
            time.sleep(0.5)
        # small pause to avoid hammering the serial port but keep updates responsive
        time.sleep(0.05)


threading.Thread(target=poll_frequency, daemon=True).start()


@app.route("/")
def index():
    html = """
    <!doctype html>
    <html>
    <head>
      <title>Yaesu CAT Control</title>
      <style>
        #freq-box, #freq-box-b {
          width: 300px; height: 100px;
          border: 2px solid #333;
          font-size: 28px;
          font-weight: bold;
          text-align: center;
          line-height: 100px;
          margin: 20px auto;
          background-color: #f0f0f0;
        }
      </style>
    </head>
    <body>
      <h1>Yaesu CAT Web Control Active</h1>
      <div id="freq-box">Loading A...</div>
      <div id="freq-box-b">Loading B...</div>
      <script>
        const boxA = document.getElementById('freq-box');
        const boxB = document.getElementById('freq-box-b');
        if (!!window.EventSource) {
          const es = new EventSource('/stream');
          es.onmessage = e => {
            try {
              const parsed = JSON.parse(e.data);
              boxA.innerText = parsed.frequency;
              boxB.innerText = parsed.frequency_b;
            } catch (err) {
              boxA.innerText = 'Error';
              boxB.innerText = 'Error';
            }
          };
          es.onerror = e => { boxA.innerText = 'Error'; boxB.innerText = 'Error'; console.error(e); };
        } else {
          async function update() {
            try {
              let r = await fetch('/freq', {cache: "no-store"});
              let j = await r.json();
              boxA.innerText = j.frequency;
              boxB.innerText = j.frequency_b;
            } catch (e) {
              boxA.innerText = "Error";
              boxB.innerText = "Error";
            }
          }
          // poll faster when EventSource is not available
          setInterval(update, 200);
          update();
        }
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/freq")
def freq():
    with latest_lock, latest_lock_b:
        return jsonify({"frequency": latest_freq, "frequency_b": latest_freq_b})


@app.route("/stream")
def stream():
    def generator():
        last_a = last_b = None
        while True:
            with latest_lock:
                cur = latest_freq
            with latest_lock_b:
                cur_b = latest_freq_b
            if cur != last_a or cur_b != last_b:
                last_a, last_b = cur, cur_b
                yield f"data: {json.dumps({'frequency': cur, 'frequency_b': cur_b})}\n\n"
            # check more frequently so UI updates faster
            time.sleep(0.05)

    return Response(stream_with_context(generator()), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
