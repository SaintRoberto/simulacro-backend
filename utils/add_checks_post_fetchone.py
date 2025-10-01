import os
import re

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
modified_files = []

assign_re = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*result\.fetchone\(\)\s*$', re.MULTILINE)
check_patterns = [
    lambda var: re.compile(r'^\s*if\s+%s\s+is\s+None\s*:' % re.escape(var)),
    lambda var: re.compile(r'^\s*if\s+not\s+%s\s*:' % re.escape(var)),
    lambda var: re.compile(r'\bcheck_row_or_abort\s*\(\s*%s\b' % re.escape(var)),
    lambda var: re.compile(r'^\s*assert\s+%s\s+is\s+not\s+None' % re.escape(var))
]

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
        out_lines = []
        i = 0
        has_import = any('from utils.db_helpers import check_row_or_abort' in l for l in lines)
        while i < len(lines):
            line = lines[i]
            m = assign_re.match(line)
            if m:
                indent, var = m.group(1), m.group(2)
                has_check = False
                for j in range(i+1, min(i+5, len(lines))):
                    nxt = lines[j]
                    if nxt.strip() == '':
                        continue
                    for patt in check_patterns:
                        if patt(var).search(nxt):
                            has_check = True
                            break
                    if has_check:
                        break
                    if re.match(r'^\s*(return|abort|raise|jsonify)\b', nxt):
                        has_check = True
                        break
                out_lines.append(line)
                if not has_check:
                    check_line = f"{indent}check_row_or_abort({var}, 'Not found', 404)\n"
                    out_lines.append(check_line)
                    changed = True
                i += 1
            else:
                out_lines.append(line)
                i += 1

        if changed:
            if not has_import:
                insert_at = 0
                while insert_at < len(out_lines) and out_lines[insert_at].strip() == '':
                    insert_at += 1
                found = False
                for idx in range(insert_at, min(len(out_lines), insert_at + 40)):
                    if re.match(r'^\s*(from|import)\s+', out_lines[idx]):
                        found = True
                    elif found and out_lines[idx].strip() == '':
                        insert_at = idx + 1
                        break
                if not found:
                    insert_at = 0
                import_line = "from utils.db_helpers import check_row_or_abort\n"
                out_lines.insert(insert_at, import_line)

            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(out_lines)
            modified_files.append(os.path.relpath(path, root))

if modified_files:
    print("Modified files:")
    for p in modified_files:
        print(p)
else:
    print("No files modified.")