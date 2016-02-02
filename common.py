import mimetypes
import subprocess
import os
import shlex
def run_command(command, on_type, on_start, context={}):
    op, *parts = command
    
    if op == 'cd':
    	os.chdir(*parts)
    	return ''

    try:
        on_type(filter(bool, sum(map(mimetypes.guess_type, parts), ())))
    except StopIteration:
        pass
    
    line = ' '.join(map(shlex.quote, command))
    print('RUNNING', line)
    proc = subprocess.Popen(line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    on_start(proc.kill)
    output, _ = proc.communicate()
    return output

is_threaded = False
is_debug = True