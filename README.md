# flask-validate

Lightweight validation for Flask request args and form data — without Flask-WTF.

Note: The purpose of this module is to provide input validation for simple Flask applications. Complex Flask applications using Flask-WTF and Flask API applications should use the input validation facilities provided by those frameworks.

Planned distribution

This project is intended to be published on PyPI. For now you can install from source (for example with `pip install -e .`). When published the package will be available as `flask-validate` on PyPI.

Recommended usage

- Use this library for small utility Flask applications and microservices where a lightweight decorator-based validation approach is sufficient.
- For larger Flask applications that use form libraries, prefer `Flask-WTF`.
- For API-focused Flask apps consider API-first frameworks or schema libraries such as `Marshmallow` or `Pydantic` which provide richer schema validation and serialization.

## What's New

- Added support for a custom error handler on validation decorators: pass `on_error` to `@validate(...)` to receive the full validation result and return any Flask response (JSON, text, etc.).
- Validation errors are now reported per-field: the `result['errors']` structure is a dictionary mapping field keys to lists of messages. The default HTML formatting includes the field name (e.g. `email: Invalid email address`).
- Examples and tests updated to demonstrate and verify the `on_error` handler and field-level errors.

## Security Audit Script

The `audit_security.py` script analyzes Flask applications to identify unprotected entry points that may accept user input without proper validation.

### Usage

```bash
# From project root
python audit_security.py <flask_app>

# Examples
python audit_security.py myapp:app
python audit_security.py tests/minimal_app.py:app
python audit_security.py path/to/my/flask/app.py:app
```

### What it checks

- ✅ **Protected routes**: Routes with `@validate()` decorators
- ⚪ **Excluded routes**: Routes with `@exclude_validation()` decorators
- ❌ **Unprotected routes**: Routes without validation that may accept user input

### Priority levels

- 🚨 **High priority**: POST/PUT/PATCH/DELETE routes without validation
- ⚠️ **Medium priority**: GET routes with parameters
- ℹ️ **Low priority**: Simple GET routes (like home pages)

### Example output

```
🔍 Flask Validate Security Audit Report
==================================================
📊 OVERALL SUMMARY:
   Total routes analyzed: 42
   ✅ Protected routes: 38
   ⚪ Excluded routes: 2
   ❌ Unprotected routes: 2
   🔒 Security Score: 95.2%

✅ PROTECTED ROUTES (have @validate decorators):
   ✓ POST /api/users
   ✓ GET /api/users/<id>

❌ UNPROTECTED ROUTES (may need validation):
   🚨 POST /api/admin (high priority)
   ℹ️  GET / (low priority)
```

### CI/CD Integration

The script exits with code 1 if high-priority unprotected routes are found, making it perfect for CI/CD pipelines:

```yaml
# In your CI/CD pipeline
- name: Security Audit
  run: python audit_security.py myapp:app
  # Will fail the build if unprotected routes exist
```