"""
Sample Flask Application Demonstrating flask-validate Library

This is a simple registration form application that showcases the use of
flask-validate for input validation in Flask applications that are not
using Flask-WTF or API frameworks.

Features demonstrated:
- Form validation with predefined rules (EMAIL, SAFE_USERNAME, etc.)
- Custom rules with set_min_max
- Error handling with HTML responses
- Success page after valid submission
"""

from flask import Flask, request, render_template_string
import sys
import os

# Add the src directory to the path to import flask_validate
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import flask_validate as fv

app = Flask(__name__)

# Example of using security monitoring
@app.route('/security-status', methods=['GET'])
@fv.exclude_validation("Security status endpoint")
def security_status():
    """Show the current security status of all routes."""
    status = fv.get_route_security_status()
    return f"""
    <h2>Route Security Status</h2>
    <p>Protected routes: {status['protected_count']}</p>
    <p>Excluded routes: {status['excluded_count']}</p>
    <p>Unprotected routes: {status['unprotected_count']}</p>
    <h3>Protected:</h3>
    <ul>{''.join(f'<li>{route}</li>' for route in status['protected'])}</ul>
    <h3>Excluded:</h3>
    <ul>{''.join(f'<li>{route}</li>' for route in status['excluded'])}</ul>
    """

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Validate Sample - Registration</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 300px; padding: 8px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>User Registration</h1>
    <p>This sample demonstrates input validation using flask-validate.</p>

    <form method="POST" action="/register">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required>
            <small>6-20 characters, letters and numbers only</small>
        </div>

        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" name="email" id="email" required>
        </div>

        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
            <small>Strong password required: 8+ characters, uppercase, lowercase, numbers, and special characters</small>
        </div>

        <div class="form-group">
            <label for="state">State (US):</label>
            <input type="text" name="state" id="state" required>
            <small>2-letter state code (e.g., CA, NY)</small>
        </div>

        <div class="form-group">
            <label for="zip">ZIP Code:</label>
            <input type="text" name="zip" id="zip" required>
        </div>

        <div class="form-group">
            <label for="age">Age:</label>
            <input type="number" name="age" id="age" required>
            <small>Must be between 18 and 120</small>
        </div>

        <div class="form-group">
            <label for="phone">Phone Number:</label>
            <input type="text" name="phone" id="phone" required>
            <small>US phone number (e.g., 555-123-4567)</small>
        </div>

        <div class="form-group">
            <label for="birthdate">Birth Date:</label>
            <input type="text" name="birthdate" id="birthdate" required>
            <small>MM/DD/YYYY format</small>
        </div>

        <button type="submit">Register</button>
    </form>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Registration Successful</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1 class="success">Registration Successful!</h1>
    <p>Thank you for registering. Here are the details you submitted:</p>
    <ul>
        <li><strong>Username:</strong> {{ username }}</li>
        <li><strong>Email:</strong> {{ email }}</li>
        <li><strong>State:</strong> {{ state }}</li>
        <li><strong>ZIP:</strong> {{ zip }}</li>
        <li><strong>Age:</strong> {{ age }}</li>
        <li><strong>Phone:</strong> {{ phone }}</li>
        <li><strong>Birth Date:</strong> {{ birthdate }}</li>
    </ul>
    <p><a href="/">Register another user</a></p>
</body>
</html>
"""

@app.route('/')
def home():
    """Display the registration form."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/register', methods=['POST'])
@fv.validate({
    'form': {
        'username': {
            'required': True,
            'rules': fv.SAFE_USERNAME  # 6-20 chars, letters/numbers
        },
        'email': {
            'required': True,
            'rules': fv.EMAIL
        },
        'password': {
            'required': True,
            'rules': fv.PASSWORD_STRONG
        },
        'state': {
            'required': True,
            'rules': fv.US_STATE  # Uses regex for state codes
        },
        'zip': {
            'required': True,
            'rules': fv.US_ZIP
        },
        'age': {
            'required': True,
            'rules': {
                'type': 'int',
                'min': 18,
                'max': 120
            }
        },
        'phone': {
            'required': True,
            'rules': fv.US_PHONE
        },
        'birthdate': {
            'required': True,
            'rules': fv.DATE
        }
    }
})
def register():
    """Handle registration form submission with validation."""
    # If we reach here, validation passed
    username = request.form['username']
    email = request.form['email']
    state = request.form['state']
    zip_code = request.form['zip']
    age = request.form['age']
    phone = request.form['phone']
    birthdate = request.form['birthdate']

    # In a real app, you'd save to database here
    # For demo, just show success page

    return render_template_string(SUCCESS_TEMPLATE,
                                username=username,
                                email=email,
                                state=state,
                                zip=zip_code,
                                age=age,
                                phone=phone,
                                birthdate=birthdate)

if __name__ == '__main__':
    print("🚀 Starting Flask Validate Sample Application with security monitoring...")

    # Check for unprotected routes before starting
    try:
        result = fv.check_unprotected_routes(app, warn_unprotected=True, fail_on_unprotected=False)
        print("✅ Security check complete:")
        print(f"   Protected routes: {len(result['protected'])}")
        print(f"   Excluded routes: {len(result['excluded'])}")
        print(f"   Unprotected routes: {len(result['unprotected'])}")

        if result['unprotected']:
            print("\n⚠️  Unprotected routes detected:")
            for route in result['unprotected']:
                print(f"   - {route['endpoint']}")

    except Exception as e:
        print(f"❌ Security check failed: {e}")

    print("\n🌐 Visit http://127.0.0.1:5000/ to see the registration form.")
    print("🌐 Visit http://127.0.0.1:5000/security-status to see route security status")
    print("Try submitting invalid data to see validation errors.")
    app.run(debug=True)