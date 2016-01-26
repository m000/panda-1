#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, Blueprint
from flask import request, redirect, render_template, url_for, send_from_directory, url_for
import sys, signal, time
import QEMUCtrl

app = Flask(__name__)
panda = None

@app.route('/')
def index():
	return 'Hello World!'

@app.route('/novnc/<vmid>')
def novnc(vmid):
	return render_template('vnc.html', vmconf=panda.conf)

# @app.route('/novnc/include/<path>')
# def novnc_static_redirect(path):
# 	'''	Redirect files loaded dynamically through javascript to the proper url.
# 	''' Use for quick debugging. Usually better solutions exist (e.g. setting INCLUDE_URI in js).
# 	return redirect(url_for('novnc.static', filename='include/%s' % (path)), code=302)

if __name__ == '__main__':
	panda = QEMUCtrl.PANDA('debian8-32')
	panda.start()

	def sigint_handler(signum, stack):
		panda.kill()
		sys.exit(0)
	signal.signal(signal.SIGINT, sigint_handler)

	# Register blueprint for noVNC static files.
	novnc_static = Blueprint('novnc', __name__, static_folder='tools/noVNC')
	app.register_blueprint(novnc_static)

	# Tell Jinja to trim empty space.
	app.jinja_env.trim_blocks = True
	app.jinja_env.lstrip_blocks = True

	# Debug info
	# print app.url_map

	# http://stackoverflow.com/q/9449101
	app.run(debug = True, use_reloader=False)
	# app.run(host='0.0.0.0', debug = True, use_reloader=False)
