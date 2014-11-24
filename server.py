import os
import sys

port = int(os.environ.get('PORT', 5001))

# check for settings file
if not os.path.isfile('local_config.py'):
    sys.exit("Local config file not found. Do cp local_config.py.git local_config.py")


if __name__ == '__main__':
    from fishing import app
    app.run(host='0.0.0.0', port=port)
