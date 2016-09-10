""" app/__init__.py
"""
from flask import Flask

from parser import build_events_list

app = Flask(__name__)

@app.route('/')
def index():
    pass
