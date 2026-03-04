"""
Vercel Serverless Function for Flask App
This handler serves the Flask application on Vercel's serverless platform.
"""

import os
import sys
from io import BytesIO
import traceback

# Add parent directory to path to import app
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(parent_dir))

# Configure database path for Vercel (use /tmp for writable storage)
# Note: SQLite on Vercel is not ideal for production due to serverless nature
# Consider using a managed database like PostgreSQL, MySQL, or MongoDB
os.environ.setdefault('DATABASE_URL', 'sqlite:////tmp/hr_demo.db')

# Import Flask - required dependency
from flask import Flask

# Import and create Flask app with error handling
# Vercel expects this to be named 'app' for automatic Flask detection
app = None
flask_app = None

try:
    from app import create_app
    app = create_app()
    flask_app = app
except Exception as e:
    # If app creation fails, create a minimal error app
    print(f"ERROR: Failed to create Flask app: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Create minimal Flask app that shows error
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        error_info = {
            'error': 'Flask app initialization failed',
            'message': str(e),
            'path': path,
            'note': 'Check Vercel logs for full traceback'
        }
        return error_info, 500
    
    flask_app = app

def handler(request):
    """
    Vercel serverless function handler for Flask app
    Converts Vercel request to WSGI and processes through Flask
    """
    try:
        # Handle different request formats (dict or object with attributes)
        if isinstance(request, dict):
            method = request.get('method', 'GET')
            path = request.get('path', '/')
            headers = request.get('headers', {})
            body = request.get('body', b'')
            query_string = request.get('queryString', '') or request.get('query_string', '')
        else:
            # Handle object-style request
            method = getattr(request, 'method', 'GET')
            path = getattr(request, 'path', '/')
            headers = getattr(request, 'headers', {})
            body = getattr(request, 'body', b'')
            query_string = getattr(request, 'queryString', '') or getattr(request, 'query_string', '')
    except Exception as e:
        # If request parsing fails, return error
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Invalid request format", "message": "{str(e)}"}}'
        }
    
    try:
        # Normalize headers to dict if needed
        if not isinstance(headers, dict):
            headers = dict(headers) if hasattr(headers, 'items') else {}
        
        # Handle body encoding
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        elif body is None:
            body_bytes = b''
        else:
            body_bytes = body
        
        # Extract host from headers safely
        host = headers.get('host', headers.get('Host', 'localhost'))
        if isinstance(host, str):
            server_name = host.split(':')[0] if ':' in host else host
            server_port = host.split(':')[1] if ':' in host else '443'
        else:
            server_name = 'localhost'
            server_port = '443'
        
        # Build WSGI environ dictionary
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'SERVER_NAME': server_name,
            'SERVER_PORT': server_port,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body_bytes),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
            'CONTENT_TYPE': headers.get('content-type', headers.get('Content-Type', '')),
            'CONTENT_LENGTH': str(len(body_bytes)),
        }
        
        # Add HTTP headers to environ
        for key, value in headers.items():
            try:
                key_upper = key.upper().replace('-', '_')
                if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ['HTTP_' + key_upper] = str(value)
            except Exception:
                # Skip invalid headers
                continue
        
        # Response storage
        response_data = []
        status_code = [200]
        response_headers = []
        
        def start_response(status, headers_list):
            try:
                status_code[0] = int(status.split()[0])
                response_headers[:] = headers_list
            except Exception as e:
                print(f"Error in start_response: {e}")
                status_code[0] = 500
                response_headers[:] = [('Content-Type', 'application/json')]
        
        # Ensure app is available
        if flask_app is None:
            raise Exception("Flask app not initialized")
        
        # Call Flask app
        app_iter = flask_app(environ, start_response)
        
        # Collect response body
        try:
            for data in app_iter:
                response_data.append(data)
        finally:
            if hasattr(app_iter, 'close'):
                try:
                    app_iter.close()
                except Exception:
                    pass
        
        # Build response body
        body_result = b''.join(response_data)
        
        # Convert headers to dict (normalize keys)
        headers_dict = {}
        for key, value in response_headers:
            try:
                # Use title case for standard headers
                key_lower = key.lower()
                if key_lower == 'content-type':
                    headers_dict['Content-Type'] = value
                elif key_lower == 'content-length':
                    headers_dict['Content-Length'] = value
                else:
                    headers_dict[key] = value
            except Exception:
                # Skip invalid header entries
                continue
        
        # Return Vercel response format
        try:
            body_str = body_result.decode('utf-8') if isinstance(body_result, bytes) else str(body_result)
        except UnicodeDecodeError:
            # If decoding fails, return as base64 or error message
            body_str = f'{{"error": "Response encoding error"}}'
            headers_dict['Content-Type'] = 'application/json'
        
        return {
            'statusCode': status_code[0],
            'headers': headers_dict,
            'body': body_str
        }
    except Exception as e:
        # Catch any unhandled exceptions
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"FUNCTION_INVOCATION_FAILED: {error_msg}")
        print(f"Traceback: {error_trace}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal server error", "message": "{error_msg}", "type": "FUNCTION_INVOCATION_FAILED"}}'
        }
