from flask import abort, make_response, jsonify

def check_row_or_abort(row, message: str = 'Not found', status: int = 404):
    """
    Abort the request with a JSON error response if `row` is None.
    Returns the row otherwise (for convenience).
    """
    if row is None:
        abort(make_response(jsonify({'error': message}), status))
    return row