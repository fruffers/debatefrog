from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Start app with "python main.py" command in terminal