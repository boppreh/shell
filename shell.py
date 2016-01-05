if __name__ == '__main__':
	import flask
	from queue import Queue
	import base64
	import json
	import subprocess
	import mimetypes
	from os.path import splitext

	app = flask.Flask(__name__)
	events_queue = Queue()
	blocks = {}

	@app.route('/')
	def root():
		return flask.send_file('index.html')

	@app.route('/outputs/<id>')
	def get_output(id):
		output, mimetype = blocks[int(id)]
		return flask.Response(output, mimetype=mimetype)

	@app.route('/run', methods=['POST'])
	def run():
		try:
			data = json.loads(flask.request.form['data'])
			first, *rest = filter(len, data['parts'])
			output = subprocess.check_output(first.split() + rest, stderr=subprocess.STDOUT)
			try:
				value = output.decode('utf-8')
			except UnicodeError:
				value = '{} bytes'.format(len(output))

			try:
				type, *_ = filter(bool, sum(map(mimetypes.guess_type, rest), ()))
			except ValueError:
				type = None
			blocks[data['id']] = (output, type)
			return get_output(data['id'])
		except Exception as e:
			return 'Shell error: {}'.format(e)

	app.run(port=80, debug=True)