import os
from main import application

if __name__ == "__main__":
    port: int = int(os.environ.get('PORT'))
    application.run(port=port, host='0.0.0.0')