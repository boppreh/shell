import common
import uncommon

import time
import flask
from queue import Queue
import base64
import json
from collections import namedtuple
import pickle
import atexit
import glob

PENDING = {'PENDING': 1}

Block = namedtuple('Block', ['input', 'output', 'inferred_type', 'kill'])

app = flask.Flask(__name__)
events_queue = Queue()
try:
    blocks = pickle.load(open('session.pickle', 'rb'))
except IOError:
    blocks = {}

@app.route('/')
def root():
    return flask.send_file('index.html')

@app.route('/glob', methods=['GET', 'POST'])
def get_glob():
    return '\n'.join(glob.glob(flask.request.args['path']))

@app.route('/file')
def get_file():
    return flask.send_file(flask.request.args['path'])

@app.route('/outputs/<id>')
def get_output(id):
    id = int(id)
    while True:
        while blocks[id].output is PENDING:
            time.sleep(0.5)

        block = blocks[id]
        result = None
        try:
            if isinstance(block.output, bytes):
                result = block.output.decode('utf-8')
        except UnicodeError as e:
            print(e)
        result = result or str(block.output)
        return flask.Response(result, mimetype=block.inferred_type)

@app.route('/remove/<id>')
def remove_output(id):
    id = int(id)
    if blocks[id].kill:
        blocks[id].kill()
    del blocks[id]
    return ''

@app.route('/session')
def get_session():
    return json.dumps({id: block.input for id, block in blocks.items()})

@app.route('/run', methods=['POST'])
def run():
    try:
        data = json.loads(flask.request.form['data'])
        id = int(data['id'])

        if id in blocks:
            remove_output(id)

        command = [p for p in data['parts'] if p]

        type = None
        def on_type(t):
            type = t
        def on_start(kill):
            blocks[id] = Block(command, PENDING, type, kill)
        def on_end(output):
            blocks[id] = Block(command, output, type, None)
        context = {id: b.output for id, b in blocks.items() if b.output is not PENDING}
        if command[0].startswith('@'):
            command[0] = command[0][1:]
            run_command = uncommon.run_command
        else:
            command = command[0].split() + command[1:]
            run_command = common.run_command
        run_command(command, on_type, on_start, on_end, context=context)

        output = blocks[id].output;
        if isinstance(output, bytes):
            try:
                return output.decode('utf-8')
            except UnicodeError:
                return ''
        return str(output)
    except Exception as e:
        return 'Shell {}: {}'.format(e.__class__.__name__, e)

def persist():
    with open('session.pickle', 'wb') as f:
        pickle.dump(blocks, f)
atexit.register(persist)

app.run(port=80, threaded=True)