if __name__ == '__main__':
	import flask
	from queue import Queue
	import base64
	import json
	import subprocess

	app = flask.Flask(__name__)
	events_queue = Queue()
	blocks = {}

	@app.route('/')
	def root():
		return flask.send_file('index.html')

	@app.route('/outputs/<id>')
	def get_output(id):
		return blocks[int(id)]

	@app.route('/run', methods=['POST'])
	def run():
		try:
			data = json.loads(flask.request.form['data'])
			first, *rest = filter(len, data['parts'])
			output = subprocess.check_output(first.split() + rest, stderr=subprocess.STDOUT)
			blocks[data['id']] = output
			try:
				return output.decode('utf-8')
			except UnicodeError:
				return '{} bytes'.format(len(output))
		except Exception as e:
			return 'Shell error: {}'.format(e)

	app.run(port=80, debug=True)