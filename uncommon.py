import mimetypes
import re

import sys
sys.path.append('../supermap')
sys.path.append('../altpython')
from altpython import replace_syntax

from supermap import BaseSupermap, FileMap
BaseSupermap.auto_expand = True
f = FileMap('.')

def run_code(src, context):
	import string
	import itertools
	import os
	from os import path

	def sum(l):
		value = None
		i = iter(l)
		while True:
			try:
				value = next(i) if value is None else value + next(i)
			except StopIteration:
				break
		return value

	replace = lambda s: re.sub(r'#(\d+)', r'context[\1]', s)
	modified_src = replace_syntax(src, replace, strip_comments=False)
	return eval(modified_src)

def run_command(command, on_type, on_start, on_end, context={}):
	if len(command) == 1:
		src, = command
		on_start(None)
		on_end(run_code(src, context))
		return

	op, path, *rest = command

	if op == 'meta':
		on_type(mimetypes.guess_type(path)[0])
		try:
			on_end('\n'.join(f[path]))
		except:
			on_end(f[path])
		return
	elif op == 'append':
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
	else:
		raise ValueError('Unexpected operator {}'.format(op))
	on_end('')

is_threaded = False
is_debug = True