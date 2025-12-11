Yaesu CAT Web Control

This repository contains a small Flask app to poll a Yaesu FTDX101MP transceiver over CAT (serial) and display receiver A and B frequencies via SSE or polling.

Quick start

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the app:

```powershell
python .\main.py
```

3. Open your browser at http://localhost:5000

Make this a GitHub repo

I initialized the repository locally (no remote set). To publish it under your GitHub account (github.com/mm5agm) create a repository on GitHub (for example named `yaesu-cat`) and then run one of the following in this project folder.

SSH (recommended if you have SSH keys):

```powershell
git remote add origin git@github.com:mm5agm/yaesu-cat.git
git branch -M main
git push -u origin main
```

HTTPS:

```powershell
git remote add origin https://github.com/mm5agm/yaesu-cat.git
git branch -M main
git push -u origin main
```

If you prefer, you can create the remote using the GitHub web UI or the `gh` CLI and then push. If you'd like, I can help create the remote automatically if you provide a GitHub personal access token or use the `gh` CLI configured on this machine.

Notes

- If you want to change polling intervals or channel behavior, edit `main.py`.
- The app expects the transceiver on `COM21`; adjust `SER_PORT` if needed.

