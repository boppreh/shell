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
		output, mimetype = blocks[id]
		return flask.Response(output, mimetype=mimetype)

	@app.route('/run', methods=['POST'])
	def run():
		try:
			data = json.loads(flask.request.form['data'])
			first, *rest = filter(len, data['parts'])
			output = subprocess.check_output(first.split() + rest, stderr=subprocess.STDOUT, shell=True)

			try:
				type = next(filter(bool, sum(map(mimetypes.guess_type, rest), ())))
			except StopIteration:
				type = None
			id = data['id']
			blocks[id] = (output, type)
			print(blocks.keys())

			return get_output(id)
		except Exception as e:
			return 'Shell {}: {}'.format(e.__class__.__name__, e)

	app.run(port=80, debug=True)