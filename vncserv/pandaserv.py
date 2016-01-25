#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, send_from_directory
import time
import QEMUCtrl

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'

@app.route('/novnc_static/<path:path>')
def novnc_static(path):
	return send_from_directory('tools/noVNC', path)

if __name__ == '__main__':
	# signal.signal(signal.SIGTERM, sigterm_handler)
	panda = QEMUCtrl.PANDA('debian8-32')
	panda.start()
	# time.sleep(5)
	# panda.kill()

	# http://stackoverflow.com/q/9449101
	app.run(debug = True, use_reloader=False)
	# app.run(host='0.0.0.0', debug = True, use_reloader=False)
