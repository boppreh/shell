import flask
from queue import Queue
import base64
import json

app = flask.Flask(__name__)
events_queue = Queue()

@app.route('/')
def root():
	return flask.send_file('index.html')

@app.route('/events')
def events(events):
	def make_events_generator():
		while True:
			yield 'event: {}\n'.format(base64.b64encode(events_queue.get()))
	return flask.Response(make_events_generator(), content_type='text/event-stream')

@app.route('/run', methods=['POST'])
def run():
	obj = json.loads(flask.request.form['data'])
	print(obj)
	return 'ok'

app.run(port=80)