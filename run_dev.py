#!/usr/bin/python
from fishing import app
import os
app.run(host="0.0.0.0", port=int(os.environ['PORT'], 5000), debug=True)
