#!/bin/bash
# update_site.sh [page_copy.html]: refresh the website's copy of the playbook after editing tools/video-render/PLAYBOOK.md.
# With a path, it also writes the copy of docs/index.html that is published on claude.ai (artifact
# Fi1TT3ivNK76xJ3ias9wHx): the same page without its doctype, html, head and body tags, which the publish adds.
# Publish it with docs/assets/*, docs/playbook.md and docs/etude1_plan.json as its files, at the same paths.
# The pictures in docs/assets/ are frames from the latest final; re-make them only when the video changes.
set -e
cd "$(dirname "$0")/.."
cp tools/video-render/PLAYBOOK.md docs/playbook.md && echo "docs/playbook.md updated"
if [ -n "$1" ]; then
  python3 - "$1" <<'PY'
import re, sys
s = open('docs/index.html').read()
s = s[s.index('<title>'):]
for tag in ['</head>\n', '<body>\n', '</body>\n', '</html>\n']:
    assert s.count(tag) == 1, tag
    s = s.replace(tag, '')
assert not re.search(r'<(html|head|body)[\s>]|</(html|head|body)>|name="viewport"|<!doctype', s, re.I)
open(sys.argv[1], 'w').write(s)
print(sys.argv[1], 'written')
PY
fi
