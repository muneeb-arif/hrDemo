"""
Run Flask app with uvicorn in watch mode
Note: Flask is WSGI, so we wrap it with WSGI-to-ASGI adapter
"""
from app import create_app
from asgiref.wsgi import WsgiToAsgi
import uvicorn
import os

# Create Flask app
flask_app = create_app()

# Wrap Flask WSGI app with ASGI adapter for uvicorn
app = WsgiToAsgi(flask_app)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    
    # Run with uvicorn in watch mode
    uvicorn.run(
        "run_uvicorn:app",  # Reference to the ASGI app
        host="0.0.0.0",
        port=port,
        reload=True,  # Watch mode - auto-reload on file changes
        reload_dirs=["./app"],  # Watch app directory for changes
        log_level="info",
        access_log=True
    )
