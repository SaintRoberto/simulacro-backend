Fix for "Cannot access attribute 'rowcount' for class 'Result[Any]'" (concise)
========================================================================

Problem
-------
Type-checkers (pyright/mypy) complain because SQLAlchemy's Result type doesn't guarantee a `rowcount` attribute in its typing.

Concise fixes (pick one)

1) Safe access (recommended - minimal change)
Replace direct usages of `result.rowcount` with:
    rowcount = getattr(result, 'rowcount', 0)
    if rowcount == 0:
        ...

This keeps runtime behavior and avoids the type-checker error.

2) Explicit cast for the type checker
If you want the checker to know it's an int:
    from typing import cast
    rowcount = cast(int, getattr(result, 'rowcount', 0))

3) Use boolean check for DML results (alternative)
If you only need to know "nothing changed", you can also check `result is None` for fetches or check `result.rowcount` at runtime but silence type-checker:
    if getattr(result, 'rowcount', 0) == 0:
        ...

Notes
-----
- `rowcount` may be None for some statement types; using `getattr(..., 0)` normalizes it to 0.
- Prefer option 1 for clarity and compatibility across the codebase.

Example replacement
-------------------
From:
    if result.rowcount == 0:
        return jsonify({'error': 'Not found'}), 404

To:
    rowcount = getattr(result, 'rowcount', 0)
    if rowcount == 0:
        return jsonify({'error': 'Not found'}), 404
