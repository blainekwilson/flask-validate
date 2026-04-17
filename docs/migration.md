# Migration Notes: field-level errors and `on_error`

Recent releases introduced two changes you should be aware of:

1. Field-level errors

- `result['errors']` is now a dictionary mapping field names to lists of messages (instead of a flat list). Update any code that inspects the old flat list accordingly. Example:

```python
# Old (legacy):
for msg in result['errors']:
    print(msg)

# New: iterate per-field
for field, messages in result['errors'].items():
    for msg in messages:
        print(f"{field}: {msg}")
```

2. `on_error` handler

- You can pass an `on_error` callable to the `@validate(...)` decorator. It receives the full `result` dict and must return a Flask response. Example:

```python
def handler(result):
    return jsonify({'errors': result['errors']}), 400

@app.route('/submit', methods=['POST'])
@fv.validate({...}, on_error=handler)
def submit():
    ...
```

Compatibility tips

- Tests and example code in this repository have been updated to assert on field-prefixed error messages when checking rendered HTML. If you programmatically inspect HTML output, prefer reading `result['errors']` in an `on_error` handler instead.
