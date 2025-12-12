# python
from pathlib import Path
import sys

# locate file relative to this script's directory
p = Path(__file__).resolve().parent / 'command_examples.txt'
if not p.exists():
    raise SystemExit(f'File not found: `{p}`')

b = p.read_bytes()
c_c3b9 = b.count(b'\xC3\xB9')
c_emdash = b.count(b'\xE2\x80\x94')

print('First 160 bytes (hex):', b[:160].hex())
print('C3 B9 count (U+00F9):', c_c3b9)
print('E2 80 94 count (em dash):', c_emdash)

try:
    text = b.decode('utf-8')
    print('\nDecoded as: utf-8')
except UnicodeDecodeError:
    text = b.decode('cp1252', errors='replace')
    print('\nDecoded as: cp1252 (fallback)')

print('\nSample lines:')
for ln in text.splitlines()[:8]:
    print(repr(ln))

if c_c3b9:
    print('\nERROR: Found remaining C3 B9 bytes.')
    sys.exit(1)
print('\nOK: no C3 B9 bytes found.')
