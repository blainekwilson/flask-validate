# 🚀 flask-validate

**Lightweight, decorator-based input validation for Flask apps — without the overhead of forms or full schema frameworks.**

---

## 🎯 Why this exists

Flask developers typically fall into two camps:

- 🧱 Full UI apps → use Flask-WTF  
- 🔌 API apps → use Marshmallow or Pydantic  

But there’s a **gap in the middle**:

> 👉 Simple Flask apps with lightweight UIs that still need safe, structured input validation

**flask-validate is built specifically for that gap.**

---

## ✨ What makes this different

- ✅ Decorator-based validation — no forms, no schemas  
- ✅ Works with query strings + form data  
- ✅ Field-level error handling  
- ✅ Custom error responses (HTML, JSON, anything)  
- 🔥 Security audit tool to detect unprotected routes  

---

## ⚡ Quick example

```python
from flask import Flask, request
import flask_validate as fv

app = Flask(__name__)

@app.route("/submit", methods=["POST"])
@fv.validate({
    "args": {
        "st": {"required": True, "rules": fv.US_STATE}
    },
    "form": {
        "zip": {"required": False, "rules": fv.US_ZIP}
    }
})
def submit():
    return f"State: {request.args['st']}"
```

---

## 🧠 Error handling (simple → advanced)

### Default (HTML response)

```python
@fv.validate(schema)
def route():
    ...
```

### Custom error handler (recommended)

```python
def json_error_handler(result):
    return {"errors": result["errors"]}, 400

@fv.validate(schema, on_error=json_error_handler)
def route():
    ...
```

### Field-level errors

```json
{
  "errors": {
    "zip": ["Invalid ZIP code"],
    "st": ["Invalid US state"]
  }
}
```

---

## 🔐 Built-in Security Audit

Find routes that accept input **without validation**.

### Run it:

```bash
python -m flask_validate app:app
```

### What it detects

- ✅ Routes protected with @validate  
- ⚪ Routes explicitly excluded  
- ❌ Routes missing validation (potential risk)  

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

❌ UNPROTECTED ROUTES:
   🚨 POST /api/admin (high priority)
   ℹ️  GET / (low priority)
```

---

## 🧩 When to use this

Use flask-validate when:

- You’re building small to mid-sized Flask apps  
- You want simple, explicit validation  
- You don’t want form libraries or heavy schemas  

---

## 🚫 When NOT to use this

- Large UI apps → use Flask-WTF  
- API-first apps → use Pydantic or Marshmallow  

---

## 📦 Installation (development)

```bash
pip install -e .
```

Planned: PyPI release as flask-validate

---

## 🛡️ Security-first design

- Inspired by OWASP validation guidance  
- Built to reduce common input validation mistakes  
- Includes runtime auditing for missing protections  

---

## 🧭 Roadmap

- [ ] PyPI release  
- [ ] Improved JSON / API support  
- [ ] Custom rule extensions  
- [ ] Enhanced reporting + CLI options  

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

---

## ⭐ Why this project stands out

Most validation libraries focus on:

- full frameworks  
- API schemas  

This one focuses on the overlooked middle.

And adds something most don’t:

> 🔥 Runtime detection of missing validation (security auditing)
