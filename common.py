import mimetypes
import subprocess
import os
def run_command(command, on_type, on_start, context={}):
    op, *parts = command
    
    if op == 'cd':
    	os.chdir(*parts)
    	return ''

    try:
        on_type(filter(bool, sum(map(mimetypes.guess_type, parts), ())))
    except StopIteration:
        pass

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    on_start(proc.kill)
    output, _ = proc.communicate()
    return output

is_threaded = False
is_debug = True