if __name__ == '__main__':
    import time
    import flask
    from queue import Queue
    import base64
    import json
    import subprocess
    import mimetypes
    from os.path import splitext
    from collections import namedtuple
    import pickle
    import atexit

    Block = namedtuple('Block', ['input', 'output', 'inferred_type', 'proc'])

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
            if not block.output:
                time.sleep(1)
                continue
            return flask.Response(block.output, mimetype=block.inferred_type)

    @app.route('/remove/<id>')
    def remove_output(id):
        id = int(id)
        if blocks[id].proc:
            blocks[id].proc.kill()
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

            if id in blocks and blocks[id].proc:
                blocks[id].proc.kill()

            if data.get('cached', False):
                return get_output(id)

            first, *rest = filter(bool, data['parts'])
            command = first.split() + rest

            try:
                type = next(filter(bool, sum(map(mimetypes.guess_type, rest), ())))
            except StopIteration:
                type = None

            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            blocks[id] = Block(command, None, type, proc)
            output, _ = proc.communicate()
            blocks[id] = Block(command, output, type, None)
            

            return get_output(id)
        except Exception as e:
            raise e
            return 'Shell {}: {}'.format(e.__class__.__name__, e)

    def persist():
        print(blocks)
        with open('session.pickle', 'wb') as f:
            pickle.dump(blocks, f)
    atexit.register(persist)

    app.run(port=80, threaded=True)