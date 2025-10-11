#!/usr/bin/env python3
"""Run Civic Eye with HTTPS for microphone access"""

import os
from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    
    # Run with HTTPS using adhoc SSL context
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=True,
        ssl_context='adhoc'  # Creates temporary SSL certificate
    )