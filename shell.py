if __name__ == '__main__':
	import flask
	from queue import Queue
	import base64
	import json
	import subprocess

	app = flask.Flask(__name__)
	events_queue = Queue()

	@app.route('/')
	def root():
		return flask.send_file('index.html')

	@app.route('/run', methods=['POST'])
	def run():
		try:
			parts = json.loads(flask.request.form['data'])
			first, *rest = filter(len, parts)
			return subprocess.check_output(first.split() + rest, stderr=subprocess.STDOUT)
		except Exception as e:
			return str(e)

	app.run(port=80, debug=True)