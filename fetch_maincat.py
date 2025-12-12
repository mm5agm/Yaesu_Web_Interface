# python
"""
Save as: `fetch_maincat.py`
Run on Windows with: python .\fetch_maincat.py
"""
import subprocess
import sys
import urllib.request
from pathlib import Path

GITHUB_RAW = "https://raw.githubusercontent.com/mm5agm/Yaesu_Web_Interface/main/mainCat.txt"
REMOTE_PATH = Path("mainCat_remote.txt")

def try_git_show() -> bool:
    # fetch origin then try to show the file from origin/main
    try:
        subprocess.run(["git", "fetch", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        # git not installed
        return False
    try:
        # Request raw bytes (text=False) to avoid automatic decoding with the locale codec.
        proc = subprocess.run(
            ["git", "--no-pager", "show", "origin/main:mainCat.txt"],
            capture_output=True,
            text=False
        )
        if proc.returncode == 0 and proc.stdout:
            # Decode bytes using utf-8 and replace undecodable bytes to avoid UnicodeDecodeError
            text = proc.stdout.decode("utf-8", errors="replace")
            REMOTE_PATH.write_text(text, encoding="utf-8")
            print(f"Saved remote `mainCat.txt` from git to `{REMOTE_PATH}`")
            return True
    except Exception:
        # any other subprocess issue -> fall back
        pass
    return False

def download_raw() -> None:
    # fallback: download raw file from GitHub
    print("Downloading raw `mainCat.txt` from GitHub...")
    with urllib.request.urlopen(GITHUB_RAW) as r:
        data = r.read().decode("utf-8", errors="replace")
    REMOTE_PATH.write_text(data, encoding="utf-8")
    print(f"Saved raw file to `{REMOTE_PATH}`")

def build_cmd(code: str, *params: str) -> str:
    # build a CAT command: two-letter code + concatenated params + ';'
    code = code.upper()
    if len(code) != 2:
        raise ValueError("code must be 2 letters")
    return f"{code}{''.join(params)};"

def parse_resp(resp: str):
    # simple parser: strip trailing ';', take first two chars as code, rest as single parameter blob
    s = resp.strip()
    if s.endswith(";"):
        s = s[:-1]
    if len(s) < 2:
        return None, []
    code = s[:2]
    rest = s[2:]
    return code, [rest] if rest else []

def main():
    ok = try_git_show()
    if not ok:
        try:
            download_raw()
        except Exception as e:
            print("Failed to fetch or download `mainCat.txt`:", e, file=sys.stderr)
            sys.exit(1)

    # print file contents (similar to PowerShell Get-Content -Raw)
    print("\n--- `mainCat_remote.txt` contents start ---\n")
    print(REMOTE_PATH.read_text(encoding="utf-8"))
    print("\n--- `mainCat_remote.txt` contents end ---\n")

    # examples of helpers
    cmd_set_fa = build_cmd("FA", "014200000")
    cmd_read_fa = build_cmd("FA")
    print("Example commands:")
    print(cmd_set_fa)
    print(cmd_read_fa)
    print("Example parse:")
    print(parse_resp("FA014200000;"))

if __name__ == "__main__":
    main()
