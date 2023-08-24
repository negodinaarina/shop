import os
from main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT'))
    app.run(port=port, host='0.0.0.0')