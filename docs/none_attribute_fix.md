Fixing "X is not a known attribute of None" (concise)
====================================================

Problem
-------
You attempted to read an attribute (for example `nombre`) from a DB row that is None because the query returned no results. Example location: [`requerimiento_respuestas/routes.py`](requerimiento_respuestas/routes.py:126).

Fix (two concise options)
-------------------------

1) Explicit null-check (minimal changes)
- Replace direct usage of a fetch result with a null-check:

  from:
  ```
  respuesta = db.session.execute(...).fetchone()
  # later...
  return jsonify({'nombre': respuesta.nombre})
  ```

  to:
  ```
  respuesta = db.session.execute(...).fetchone()
  if respuesta is None:
      return jsonify({'error': 'Not found'}), 404
  return jsonify({'nombre': respuesta.nombre})
  ```

  Example occurrence: [`requerimiento_respuestas/routes.py`](requerimiento_respuestas/routes.py:126)

2) Centralized helper (recommended for consistency)
- Use the helper added at [`utils/db_helpers.py`](utils/db_helpers.py:1):

  from utils.db_helpers import check_row_or_abort

  respuesta = db.session.execute(...).fetchone()
  check_row_or_abort(respuesta, 'Respuesta no encontrada', 404)
  # now safe to use respuesta.nombre

Why this fixes it
-----------------
If the DB returns no row, fetchone() returns None. Accessing attributes on None raises the error. The check aborts/returns early so later attribute access is safe.

Suggested rollout
-----------------
- Prefer option 2 for consistency: import `check_row_or_abort` and apply after each `.fetchone()` where the code previously assumed a row existed.
- Grep for `.fetchone()` and add checks in the same file(s). Example search: `fetchone()` and `if row is None` patterns.

Files to update (examples)
--------------------------
- [`requerimiento_respuestas/routes.py`](requerimiento_respuestas/routes.py:109)
- [`usuarios/routes.py`](usuarios/routes.py:126)
- Any other file that calls `.fetchone()` and then immediately reads attributes (search: `fetchone()`).
