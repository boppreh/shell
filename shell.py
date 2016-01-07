#from common import run_command, is_threaded, is_debug
from uncommon import run_command, is_threaded, is_debug

if __name__ == '__main__':
    import time
    import flask
    from queue import Queue
    import base64
    import json
    from collections import namedtuple
    import pickle
    import atexit

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

    @app.route('/outputs/<id>')
    def get_output(id):
        while True:
            block = blocks[int(id)]
            while block.output is None:
                time.sleep(0.5)
                continue
            return flask.Response(block.output, mimetype=block.inferred_type)

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

            if data.get('cached', False):
                return get_output(id)

            if id in blocks:
                remove_output(id)

            first, *rest = filter(bool, data['parts'])
            command = first.split() + rest
            type = None

            def on_type(t):
                type = t
            def on_start(kill):
                blocks[id] = Block(command, None, type, kill)
            def on_end(output):
                blocks[id] = Block(command, output, type, None)
            run_command(command, on_type, on_start, on_end)
            return get_output(id)
        except Exception as e:
            raise e
            return 'Shell {}: {}'.format(e.__class__.__name__, e)

    def persist():
        with open('session.pickle', 'wb') as f:
            pickle.dump(blocks, f)
    atexit.register(persist)

    app.run(port=80, debug=is_debug, threaded=is_threaded)