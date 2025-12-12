# python
from pathlib import Path
import shutil

p = Path('YaesuCat') / 'command_examples.txt'
if not p.exists():
    raise SystemExit(f'File not found: `{p}`')

# backup
bak = p.with_suffix('.txt.bak')
shutil.copy2(p, bak)

text = p.read_text(encoding='utf-8')
if '\u00f9' in text:
    text = text.replace('\u00f9', '—')
    p.write_text(text, encoding='utf-8')
    print(f'Fixed `{p}` (backup: `{bak.name}`).')
else:
    print('No U+00F9 found; no changes made.')
