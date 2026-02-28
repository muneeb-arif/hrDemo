from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Use port from environment variable or default to 5001 (5000 is often used by AirPlay on macOS)
    port = int(os.getenv('FLASK_PORT', 5001))
    
    # Option 1: Flask's built-in development server (with auto-reload)
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True)
    
    # Option 2: To use uvicorn instead, run: python run_uvicorn.py
    # Or: uvicorn run_uvicorn:app --reload --host 0.0.0.0 --port 5001
