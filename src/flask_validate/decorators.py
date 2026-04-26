"""
decorators.py

Flask decorator interface for request validation.

This module integrates the core validation engine with Flask by:
- extracting request data
- invoking the validator
- handling error responses
- providing security monitoring for unprotected endpoints
"""

import inspect
import warnings
from functools import wraps
from flask import request, make_response, current_app, g

from .validator import validate_request_data
from .errors import format_error_response


# Global registry for tracking protected/unprotected routes
_route_registry = {
    'protected': set(),
    'excluded': set(),
    'unprotected': set()
}


def exclude_validation(reason="Endpoint does not require input validation"):
    """
    Decorator to explicitly exclude an endpoint from validation requirements.

    Use this for endpoints that genuinely don't accept user input, such as:
    - Health check endpoints
    - Static pages
    - API documentation endpoints
    - Authentication endpoints that handle their own validation

    :param reason: Reason for excluding validation (for documentation)
    :type reason: str
    """
    def decorator(func):
        # Mark this function as excluded from validation
        func.__validation_excluded__ = True
        func.__validation_exclude_reason__ = reason

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add to excluded registry
            endpoint = f"{request.method} {request.path}"
            _route_registry['excluded'].add(endpoint)

            return func(*args, **kwargs)

        # Mirror exclusion attributes on the returned wrapper so route inspection
        # (before any requests) can detect the exclusion.
        wrapper.__validation_excluded__ = True
        wrapper.__validation_exclude_reason__ = reason
        wrapper._flask_validate_excluded = True
        # Keep reference to original for chained decorators
        wrapper.__original_func__ = func

        return wrapper
    return decorator


def validate_request(rules, on_error=None):
    """
    Flask decorator for validating incoming request data.

    This decorator is designed to work correctly when stacked with other decorators
    by preserving function metadata and performing validation early in the call chain.

    Example usage:
        @app.route('/submit', methods=['POST'])
        @other_decorator  # Runs first
        @validate({...})  # Validation runs second
        def submit_form():
            return "Success"

    :param rules: Validation rules dictionary
    :type rules: dict
    :param on_error: Optional callable that accepts the full validation result dict and returns a Flask response
    :type on_error: callable | None
    """

    def decorator(func):
        # Store reference to original function for inspection if needed
        original_func = func

        # Mark this function as protected
        func.__validation_protected__ = True
        func.__validation_rules__ = rules

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add to protected registry
            endpoint = f"{request.method} {request.path}"
            _route_registry['protected'].add(endpoint)

            # Extract request data - do this early before other decorators can modify
            request_data = {
                "form": request.form,
                "query_string": request.args,
                "cookie": request.cookies,
                "header": request.headers,
                "method": request.method,
            }

            try:
                # Run validation
                result = validate_request_data(rules, request_data)

                if not result["valid"]:
                    if on_error:
                        return on_error(result)
                    html = format_error_response(result)
                    response = make_response(html)
                    response.status_code = 400
                    return response

                # Call the original function
                return func(*args, **kwargs)

            except Exception as e:
                # Re-raise exceptions to maintain normal error handling
                # This ensures other decorators can still handle exceptions properly
                raise

        # Store original function on wrapper for inspection by other decorators
        wrapper.__original_func__ = original_func
        wrapper.__validation_rules__ = rules
        # Mark wrapper as protected for external checks and backward compatibility
        wrapper._flask_validate_protected = True

        return wrapper

    return decorator


def check_unprotected_routes(app=None, warn_unprotected=True, fail_on_unprotected=False):
    """
    Check for unprotected Flask routes that may accept user input.

    This function scans all registered routes and identifies those that:
    - Accept POST/PUT/PATCH methods (likely to receive user input)
    - Are not decorated with @validate or @exclude_validation

    :param app: Flask app instance (uses current_app if None)
    :param warn_unprotected: Whether to emit warnings for unprotected routes
    :param fail_on_unprotected: Whether to raise an exception for unprotected routes
    :return: Dict with protected, excluded, and unprotected routes
    :raises: RuntimeError if fail_on_unprotected=True and unprotected routes found
    """
    if app is None:
        app = current_app

    unprotected_routes = []
    protected_list = []
    excluded_list = []

    def _resolve_original(f):
        # Walk any wrapper chain to the original function, if present
        seen = set()
        while hasattr(f, '__original_func__') and id(f) not in seen:
            seen.add(id(f))
            f = getattr(f, '__original_func__')
        return f

    with app.app_context():
        for rule in app.url_map.iter_rules():
            # Skip static routes and HEAD/OPTIONS methods
            if rule.endpoint == 'static' or rule.rule == '/static/<path:filename>':
                continue

            for method in rule.methods:
                if method in ('HEAD', 'OPTIONS'):
                    continue

                endpoint = f"{method} {rule.rule}"

                # Prefer explicit runtime registry entries if present
                if endpoint in _route_registry['protected']:
                    protected_list.append(endpoint)
                    continue
                if endpoint in _route_registry['excluded']:
                    excluded_list.append(endpoint)
                    continue

                # Inspect the Flask view function for decorator-set attributes
                view_func = app.view_functions.get(rule.endpoint)
                resolved = _resolve_original(view_func) if view_func else None

                is_protected = False
                is_excluded = False

                if view_func is not None:
                    if getattr(view_func, '_flask_validate_protected', False) or getattr(view_func, '__validation_protected__', False):
                        is_protected = True
                    if getattr(view_func, '_flask_validate_excluded', False) or getattr(view_func, '__validation_excluded__', False):
                        is_excluded = True

                if not (is_protected or is_excluded) and resolved is not None and resolved is not view_func:
                    # Check attributes on resolved/original function as well
                    if getattr(resolved, '_flask_validate_protected', False) or getattr(resolved, '__validation_protected__', False):
                        is_protected = True
                    if getattr(resolved, '_flask_validate_excluded', False) or getattr(resolved, '__validation_excluded__', False):
                        is_excluded = True

                if is_protected:
                    protected_list.append(endpoint)
                    continue
                if is_excluded:
                    excluded_list.append(endpoint)
                    continue

                # Consider routes that accept user input as potentially unprotected
                if method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                    # POST/PUT/PATCH/DELETE routes are more likely to accept user input
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': True
                    })
                elif method == 'GET' and '<' in rule.rule:
                    # GET routes with parameters might need validation
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': True
                    })
                elif method == 'GET':
                    # GET routes without parameters are less likely to need validation, but still track them
                    unprotected_routes.append({
                        'endpoint': endpoint,
                        'method': method,
                        'rule': rule.rule,
                        'likely_input_route': False
                    })

    if unprotected_routes and warn_unprotected:
        warnings.warn(
            f"Found {len(unprotected_routes)} potentially unprotected routes that may accept user input:\n" +
            "\n".join([f"  - {route['endpoint']}" for route in unprotected_routes]) +
            "\n\nConsider adding @validate() decorators or @exclude_validation() for routes that don't need validation.",
            UserWarning,
            stacklevel=2
        )

    if unprotected_routes and fail_on_unprotected:
        raise RuntimeError(
            f"Found {len(unprotected_routes)} unprotected routes. "
            "Add @validate() decorators or @exclude_validation() decorators as appropriate."
        )
    
    return {
        'protected': sorted(protected_list),
        'excluded': sorted(excluded_list),
        'unprotected': sorted(unprotected_routes, key=lambda r: r['endpoint'])
    }


def get_route_security_status():
    """
    Get the current security status of all registered routes.

    :return: Dict with route security information
    """
    # Build an accurate status by scanning the app routes via check_unprotected_routes
    try:
        result = check_unprotected_routes(warn_unprotected=False)
    except TypeError:
        # Older call-sites may not pass app; ensure current_app is used by check_unprotected_routes
        result = check_unprotected_routes(None, warn_unprotected=False)

    return {
        'protected_count': len(result.get('protected', [])),
        'excluded_count': len(result.get('excluded', [])),
        'unprotected_count': len(result.get('unprotected', [])),
        'protected': result.get('protected', []),
        'excluded': result.get('excluded', []),
        'unprotected': result.get('unprotected', [])
    }