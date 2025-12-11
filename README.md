Yaesu Web Interface

This project provides a small Flask web interface to control a Yaesu FTDX101MP via CAT commands.

Updates made:
- Added a `YaesuCat` Python package that provides command mnemonics and helper functions: `YaesuCat.protocol` and `YaesuCat.yaesu_cat`.
- The web UI now uses Server-Sent Events (SSE) to update frequencies for VFO A and B in real-time.
- Added `/set_freq` POST endpoint to set FA/FB (JSON body: {"vfo":"FA","hz":14250000}).
- Added unit tests for the protocol module and a GitHub Actions workflow to run tests on push.

Quick start

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the app:

```powershell
python main.py
```

3. Open http://localhost:5000 in a browser.

Notes
- Serial port is configured with `SER_PORT` and `SER_BAUD` at the top of `main.py`.
- If your environment has an existing `YaesuCat` file, this repo now includes a proper `YaesuCat` package to avoid conflicts.

