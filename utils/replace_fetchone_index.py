import os
import re

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
modified = []

pattern = re.compile(r'^([ \\t]*)([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*result\\.fetchone\\(\\)\\[0\\]\\s*$', re.MULTILINE)

for dirpath, dirnames, filenames in os.walk(root):
    if any(p in dirpath for p in ('venv', '.venv', '__pycache__')):
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                s = f.read()
        except Exception:
            continue
        new, n = pattern.subn(
            lambda m: (
                f"{m.group(1)}row = result.fetchone()\n"
                f"{m.group(1)}if row is None:\n"
                f"{m.group(1)}    return jsonify({{'error': 'Insert failed'}}), 500\n"
                f"{m.group(1)}{m.group(2)} = row[0]"
            ),
            s
        )
        if n:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            modified.append(os.path.relpath(path, root))

if modified:
    print("Modified files:")
    for m in modified:
        print(m)
else:
    print("No files modified.")