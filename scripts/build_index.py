#!/usr/bin/env python3
"""Rebuild index.html = src/index.template.html with __SKILLS__ replaced by data/skills.json.

Only needed after changing the template or data/skills.json.
Trends and weekly issues are fetched at runtime from data/live.json and weeks/*.json, so a
data-only change needs no rebuild.

  python3 scripts/build_index.py                  # writes index.html
  python3 scripts/build_index.py --offline out.html   # standalone copy that reads data from the live site
"""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = 'https://miyam4a1.github.io/ai-radar/'
t = (ROOT / 'src/index.template.html').read_text()
sk = json.loads((ROOT / 'data/skills.json').read_text())
html = t.replace('__SKILLS__', json.dumps(sk, ensure_ascii=False))
if '--offline' in sys.argv:
    out = pathlib.Path(sys.argv[sys.argv.index('--offline') + 1])
    o = html.replace("const BASE='';", f"const BASE='{LIVE}';")
    assert o != html, 'BASE marker not found in template'
    out.write_text(o); print('wrote', out)
else:
    (ROOT / 'index.html').write_text(html); print('wrote index.html,', len(sk), 'skills')
