# Flask Validate Examples

This directory contains sample applications demonstrating the use of the flask-validate library.

## Sample Registration App

`sample_registration_app.py` - A complete Flask application showing user registration with input validation.

### Features Demonstrated

- **Form Validation**: Using the `@fv.validate` decorator on POST routes
- **Predefined Rules**: EMAIL, SAFE_USERNAME, PASSWORD_STRONG, US_STATE, US_ZIP
- **Custom Rules**: Integer validation with min/max for age
- **Error Handling**: Automatic HTML error responses for invalid input
- **Success Handling**: Custom success page after valid submission
 - **Custom Error Handlers**: Demonstrates how to pass an `on_error` callable to `@fv.validate(...)` to return custom responses (JSON, plain-text, etc.).

### How to Run

1. Ensure Flask is installed: `pip install flask`
2. Navigate to the examples directory
3. Run the app: `python sample_registration_app.py`
4. Open http://127.0.0.1:5000/ in your browser
5. Try submitting the form with valid and invalid data to see validation in action

### New example: `example_on_error.py`

`example_on_error.py` demonstrates the `on_error` handler and includes a small HTML UI. Run it and POST to `/demo_on_error` (or open the GET form at `/demo_on_error`) to see a custom plain-text error message returned when validation fails.

### Validation Rules Used

- **Username**: 6-20 characters, letters and numbers only
- **Email**: Valid email format
- **Password**: Strong password requirements (from OWASP patterns)
- **State**: Valid 2-letter US state code
- **ZIP**: Valid US ZIP code format
- **Age**: Integer between 18 and 120
- **Phone**: Valid US phone number format (e.g., 555-123-4567)
- **Birth Date**: Valid US date format with leap year support (MM/DD/YYYY)

### Code Structure

The app uses inline HTML templates for simplicity. In a real application, you'd use Jinja2 templates from files.

The validation decorator automatically:
- Checks form data against the specified rules
- Returns a 400 Bad Request with HTML error list if validation fails
- Allows the route function to execute if validation passes</content>
<parameter name="filePath">/Users/blaine/Documents/Projects/Python/flask-validate/examples/README.md