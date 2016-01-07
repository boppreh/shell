import subprocess
def run_command(command, on_start, on_end):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    on_start(proc)
    output, _ = proc.communicate()
    on_end(output)

import mimetypes
def guess_mime_type(parts):
    try:
        return next(filter(bool, sum(map(mimetypes.guess_type, parts), ())))
    except StopIteration:
        return None