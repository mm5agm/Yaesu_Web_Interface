from typing import Optional, Any as _Any
try:
    from flask import Flask, render_template_string, jsonify, Response, stream_with_context, request
except Exception:
    # Fallbacks for static analysis / IDEs that haven't indexed the venv yet
    Flask = _Any
    render_template_string = _Any
    jsonify = _Any
    Response = _Any
    stream_with_context = _Any
    request = _Any
import serial
import threading
import time
import json
import logging
import os

# configure simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the YaesuCat package; fall back gracefully if missing
yaesu_protocol = None
try:
    from YaesuCat import protocol as yaesu_protocol  # type: ignore
    logger.info("Imported YaesuCat.protocol successfully")
except Exception as e:
    logger.warning("YaesuCat.protocol not available, falling back to simple ASCII commands: %s", e)
    yaesu_protocol = None

app = Flask(__name__)

SER_PORT = "COM21"
SER_BAUD = 38400

ser: Optional[serial.Serial] = None
latest_freq = "Unknown"
latest_freq_b = "Unknown"
# single lock for protecting latest values
latest_lock = threading.Lock()
# single lock for serial access
serial_lock = threading.Lock()

# Helper wrappers so code works whether yaesu_protocol is present or not
import re

def _build_get_cmd(vfo: str) -> bytes:
    if yaesu_protocol is not None:
        return yaesu_protocol.build_get_freq(vfo)
    return f"{vfo};".encode("ascii")


def _build_set_cmd(vfo: str, hz: int) -> bytes:
    if yaesu_protocol is not None:
        return yaesu_protocol.build_set_freq(vfo, hz)
    # fallback: 9-digit ASCII payload
    return f"{vfo}{int(hz):09d};".encode("ascii")


def _parse_hz_resp(resp: bytes) -> int:
    if yaesu_protocol is not None:
        return yaesu_protocol.parse_freq_response(resp)
    m = re.search(rb"(\d{9})", resp)
    if not m:
        raise ValueError("no 9-digit frequency found in response")
    return int(m.group(1))


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
                timeout=0.15,
            )
            return
        except (serial.SerialException, OSError):
            ser = None
            time.sleep(backoff)
            backoff = min(10.0, backoff * 2)


def _hz_to_display(hz: int) -> str:
    mhz = hz / 1_000_000
    return f"{mhz:.5f} MHz"


def _serial_readline(s: serial.Serial) -> bytes:
    """Read until b';' if available, else fallback to readline(). Return raw bytes."""
    # prefer read_until if available
    if hasattr(s, "read_until"):
        try:
            return s.read_until(b";")
        except Exception:
            pass
    # fallback
    try:
        return s.readline()
    except Exception:
        return b""


def poll_frequency() -> None:
    global ser, latest_freq, latest_freq_b
    while True:
        try:
            # ensure we have a serial instance open
            if ser is None or not getattr(ser, "is_open", False):
                open_serial()

            # Use local reference
            s = ser
            if s is None:
                time.sleep(0.02)
                continue

            # Query both receivers quickly while holding the serial lock
            with serial_lock:
                # flush input buffer if available
                if hasattr(s, "reset_input_buffer"):
                    try:
                        s.reset_input_buffer()
                    except Exception:
                        pass
                elif hasattr(s, "flushInput"):
                    try:
                        s.flushInput()
                    except Exception:
                        pass

                # Query frequency A
                s.write(_build_get_cmd("FA"))
                raw = _serial_readline(s)

                # Query frequency B
                s.write(_build_get_cmd("FB"))
                raw_b = _serial_readline(s)

            # parse outside lock; use protocol parser for strict 9-digit extraction
            if raw:
                try:
                    hz = _parse_hz_resp(raw)
                    parsed = _hz_to_display(hz)
                except Exception:
                    # fallback to best-effort decode
                    try:
                        parsed = raw.decode(errors="ignore").strip()
                    except Exception:
                        parsed = "Invalid"
                with latest_lock:
                    latest_freq = parsed

            if raw_b:
                try:
                    hz_b = _parse_hz_resp(raw_b)
                    parsed_b = _hz_to_display(hz_b)
                except Exception:
                    try:
                        parsed_b = raw_b.decode(errors="ignore").strip()
                    except Exception:
                        parsed_b = "Invalid"
                with latest_lock:
                    latest_freq_b = parsed_b

        except (serial.SerialException, OSError) as e:
            with latest_lock:
                latest_freq = f"Error: {e}"
                latest_freq_b = f"Error: {e}"
            try:
                if ser is not None and hasattr(ser, "close"):
                    ser.close()
            except Exception:
                pass
            ser = None
            time.sleep(0.5)
        # small pause to avoid hammering the serial port but keep updates responsive
        time.sleep(0.02)


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
        .controls { text-align:center; margin: 10px; }
        .controls input { width: 200px; font-size: 18px; }
        .controls button { font-size: 16px; }
      </style>
    </head>
    <body>
      <h1>Yaesu CAT Web Control Active</h1>
      <div id="freq-box">Loading A...</div>
      <div class="controls">
        <input id="freq-input-a" type="number" placeholder="Hz (e.g. 14250000)" />
        <button id="set-a">Set A</button>
      </div>
      <div id="freq-box-b">Loading B...</div>
      <div class="controls">
        <input id="freq-input-b" type="number" placeholder="Hz (e.g. 7100000)" />
        <button id="set-b">Set B</button>
      </div>
      <script>
        const boxA = document.getElementById('freq-box');
        const boxB = document.getElementById('freq-box-b');
        const inputA = document.getElementById('freq-input-a');
        const inputB = document.getElementById('freq-input-b');
        const setA = document.getElementById('set-a');
        const setB = document.getElementById('set-b');

        async function setFreq(vfo, hz) {
          try {
            const r = await fetch('/set_freq', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ vfo: vfo, hz: parseInt(hz, 10) })
            });
            const j = await r.json();
            if (!r.ok) throw new Error(j.reason || 'set failed');
            return true;
          } catch (e) {
            console.error(e);
            return false;
          }
        }

        setA.addEventListener('click', async () => {
          if (!inputA.value) return alert('Enter Hz for A');
          const ok = await setFreq('FA', inputA.value);
          if (ok) alert('Set A');
        });
        setB.addEventListener('click', async () => {
          if (!inputB.value) return alert('Enter Hz for B');
          const ok = await setFreq('FB', inputB.value);
          if (ok) alert('Set B');
        });

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
    with latest_lock:
        return jsonify({"frequency": latest_freq, "frequency_b": latest_freq_b})


@app.route("/stream")
def stream():
    def generator():
        last_a = last_b = None
        while True:
            with latest_lock:
                cur = latest_freq
                cur_b = latest_freq_b
            if cur != last_a or cur_b != last_b:
                last_a, last_b = cur, cur_b
                yield f"data: {json.dumps({'frequency': cur, 'frequency_b': cur_b})}\n\n"
            # check more frequently so UI updates faster
            time.sleep(0.05)

    return Response(stream_with_context(generator()), mimetype="text/event-stream")


@app.route('/set_freq', methods=['POST'])
def set_freq():
    """Set frequency for FA or FB. JSON body: {"vfo": "FA"|"FB", "hz": 14250000} """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "reason": "missing json"}), 400
    vfo = data.get('vfo')
    hz = data.get('hz')
    if vfo not in ('FA', 'FB'):
        return jsonify({"status": "error", "reason": "invalid vfo"}), 400
    try:
        hz = int(hz)
    except Exception:
        return jsonify({"status": "error", "reason": "invalid hz"}), 400

    cmd = _build_set_cmd(vfo, hz)
    # do serial write under lock
    with serial_lock:
        if ser is None or not getattr(ser, 'is_open', False):
            try:
                open_serial()
            except Exception:
                pass
        if ser is None:
            return jsonify({"status": "error", "reason": "serial unavailable"}), 503
        try:
            ser.write(cmd)
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "reason": str(e)}), 500


if __name__ == "__main__":
    # Allow overriding host/port via environment variables (FLASK_RUN_HOST/FLASK_RUN_PORT or HOST/PORT)
    host = os.environ.get("FLASK_RUN_HOST") or os.environ.get("HOST") or "192.168.0.100"
    port = int(os.environ.get("FLASK_RUN_PORT") or os.environ.get("PORT") or 5000)
    logger.info("Starting Flask app on %s:%s", host, port)
    try:
        app.run(host=host, port=port)
    except OSError as e:
        logger.exception("Failed to bind to %s:%s: %s", host, port, e)
        raise
