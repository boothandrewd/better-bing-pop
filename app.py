""" app/__init__.py
"""
from flask import Flask, render_template

from parser import build_events_list

server = Flask(__name__)

@server.route('/')
def index():
    return render_template('index.j2', events_list=build_events_list())
