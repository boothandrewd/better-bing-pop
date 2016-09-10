""" __init__.py
"""
import json

from flask import Flask, render_template
from flask_redis import FlaskRedis

server = Flask(__name__)
redis = FlaskRedis(server)

@server.route('/')
def index():
    return render_template('index.j2', events_list=json.loads(redis.get('events_list').decode('utf-8')))
