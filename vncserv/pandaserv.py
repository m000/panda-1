#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, send_from_directory
import sys, signal, time
import QEMUCtrl

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'

@app.route('/novnc_static/<path:path>')
def novnc_static(path):
	return send_from_directory('tools/noVNC', path)

if __name__ == '__main__':
	panda = QEMUCtrl.PANDA('debian8-32')
	panda.start()

	def sigint_handler(signum, stack):
		panda.kill()
		sys.exit(0)
	signal.signal(signal.SIGINT, sigint_handler)

	# http://stackoverflow.com/q/9449101
	app.run(debug = True, use_reloader=False)
	# app.run(host='0.0.0.0', debug = True, use_reloader=False)
