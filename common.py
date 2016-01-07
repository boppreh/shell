import mimetypes
import subprocess
def run_command(command, on_type, on_start, on_end, context={}):
    op, *parts = command
    try:
        on_type(filter(bool, sum(map(mimetypes.guess_type, parts), ())))
    except StopIteration:
        pass

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    on_start(proc.kill)
    output, _ = proc.communicate()
    on_end(output)

is_threaded = False
is_debug = True