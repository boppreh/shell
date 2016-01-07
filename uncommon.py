import mimetypes

import sys
sys.path.append('../supermap')

from supermap import BaseSupermap, FileMap
BaseSupermap.auto_expand = True
f = FileMap()

def run_command(command, on_type, on_start, on_end):
	op, path, *rest = command

	if op == 'meta':
		on_type(mimetypes.guess_type(path)[0])
		try:
			on_end('\n'.join(f[path]))
		except:
			on_end(f[path])
		return

	if op == 'append':
		dst, = rest
		if f.isdir(path):
			f[dst] = f[path]
		else:
			f[dst] = f[dst] + f[path]
	elif op == 'clear':
		assert not rest
		if f.isdir(path):
			for k in f[path]:
				del f[path]
		else:
			f[path] = ''
	elif op == 'remove':
		assert not rest
		del f[path]
	elif op == 'exec':
		params, = rest
		raise NotImplementedError()
	on_end('')

is_threaded = False
is_debug = True