import os
from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

# Run this manually once in a Python console to seed an authority/admin account:
# from storage.db import CivicDB
# db = CivicDB()
# db.create_user("authority1", "auth@civic.com", "password", "Authority User", "authority")
