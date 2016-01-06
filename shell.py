if __name__ == '__main__':
	import flask
	from queue import Queue
	import base64
	import json
	import subprocess
	import mimetypes
	from os.path import splitext
	from collections import namedtuple

	Block = namedtuple('Block', ['input', 'output', 'inferred_type'])

	app = flask.Flask(__name__)
	events_queue = Queue()
	blocks = {}

	@app.route('/')
	def root():
		return flask.send_file('index.html')

	@app.route('/outputs/<id>')
	def get_output(id):
		block = blocks[id]
		return flask.Response(block.output, mimetype=block.inferred_type)

	@app.route('/remove/<id>')
	def remove_output(id):
		del blocks[id]

	@app.route('/session')
	def get_session():
		return json.dumps({id: block.input for id, block in blocks.items()})

	@app.route('/run', methods=['POST'])
	def run():
		try:
			data = json.loads(flask.request.form['data'])
			id = str(data['id'])
			if data.get('cached', False):
				return get_output(id)

			first, *rest = filter(len, data['parts'])
			command = first.split() + rest
			output = subprocess.check_output(command,
				stderr=subprocess.STDOUT,
				shell=True)

			try:
				type = next(filter(bool, sum(map(mimetypes.guess_type, rest), ())))
			except StopIteration:
				type = None

			blocks[id] = Block(command, output, type)
			print(repr(id))

			return get_output(id)
		except Exception as e:
			return 'Shell {}: {}'.format(e.__class__.__name__, e)

	app.run(port=80, debug=True)