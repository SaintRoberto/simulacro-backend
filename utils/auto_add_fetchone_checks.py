import os
import re

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
modified = []

pattern = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?\.fetchone\(\))(?:\s*\[0\])?\s*$', re.MULTILINE)

for dirpath, dirnames, filenames in os.walk(root):
    if any(p in dirpath for p in ('venv', '.venv', '__pycache__')):
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        if os.path.normpath(path).endswith(os.path.normpath('utils/db_helpers.py')):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            continue

        changed = False
        out = []
        i = 0
        has_import = any('from utils.db_helpers import check_row_or_abort' in l for l in lines)
        while i < len(lines):
            line = lines[i]
            m = pattern.match(line)
            if m:
                indent, var, rhs = m.group(1), m.group(2), m.group(3)
                has_check = False
                # look ahead up to 5 lines for an existing check
                for j in range(i+1, min(len(lines), i+6)):
                    nxt = lines[j]
                    if nxt.strip() == '':
                        continue
                    if re.search(r'\bcheck_row_or_abort\s*\(\s*%s\b' % re.escape(var), nxt):
                        has_check = True
                        break
                    if re.match(r'^\s*if\s+%s\s+is\s+None\s*:' % re.escape(var), nxt):
                        has_check = True
                        break
                    if re.match(r'^\s*if\s+not\s+%s\s*:' % re.escape(var), nxt):
                        has_check = True
                        break
                    if re.match(r'^\s*assert\s+%s\s+is\s+not\s+None' % re.escape(var), nxt):
                        has_check = True
                        break
                    if re.match(r'^\s*(return|abort|raise|jsonify)\b', nxt):
                        has_check = True
                        break
                # handle fetchone()[0] patterns by detecting literal [0] in the line
                if '[0]' in line:
                    out.append(f"{indent}row = {rhs}\n")
                    out.append(f"{indent}if row is None:\n")
                    out.append(f"{indent}    return jsonify({{'error': 'Not found'}}), 404\n")
                    out.append(f"{indent}{var} = row[0]\n")
                    changed = True
                else:
                    out.append(line)
                    if not has_check:
                        out.append(f"{indent}check_row_or_abort({var}, 'Not found', 404)\n")
                        changed = True
                i += 1
            else:
                out.append(line)
                i += 1

        if changed:
            if not has_import:
                insert_at = 0
                while insert_at < len(out) and out[insert_at].strip() == '':
                    insert_at += 1
                found = False
                for idx in range(insert_at, min(len(out), insert_at + 40)):
                    if re.match(r'^\s*(from|import)\s+', out[idx]):
                        found = True
                    elif found and out[idx].strip() == '':
                        insert_at = idx + 1
                        break
                if not found:
                    insert_at = 0
                out.insert(insert_at, "from utils.db_helpers import check_row_or_abort\n")
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(out)
            modified.append(os.path.relpath(path, root))

if modified:
    print("Modified files:")
    for p in modified:
        print(p)
else:
    print("No files modified.")