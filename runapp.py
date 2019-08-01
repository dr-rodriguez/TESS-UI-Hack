from app.app import app_portal
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app_portal.run(host='0.0.0.0', port=port, debug=False)
