""" worker.py
"""
from time import sleep
import json

from app import redis
from parser import build_events_list

while True:
    redis.set('events_list', json.dumps(build_events_list()))
    sleep(60*15)
