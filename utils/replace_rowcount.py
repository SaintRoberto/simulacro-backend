import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
modified = []

for dirpath, dirnames, filenames in os.walk(root):
    # skip virtual env folders just in case
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
        if 'getattr(result, 'rowcount', 0)' in s:
            new = s.replace("getattr(result, 'rowcount', 0)", "getattr(result, 'rowcount', 0)")
            if new != s:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new)
                modified.append(os.path.relpath(path, root))

if modified:
    print("Modified files:")
    for m in modified:
        print(m)
else:
    print("No files modified.")