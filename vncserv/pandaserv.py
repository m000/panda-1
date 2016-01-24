#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'

@app.route('/novnc/<path:path>')
def novnc_static(path):
	return send_from_directory('tools/noVNC', path)

# Btrfs × cp --reflink

if __name__ == '__main__':
	app.run(debug = True)
	# app.run(host='0.0.0.0')