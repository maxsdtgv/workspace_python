import sys
import time
import shlex
from subprocess import PIPE, Popen
from threading  import Thread

try:
	from queue import Queue, Empty
except ImportError:
	from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
	for line in iter(out.readline, b''):
		queue.put(line)
	out.close()

str3 = 'ping 8.8.8.8 -r'

p = Popen(shlex.split(str3), stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()
time.sleep(1)
# ... do other things here

# read line without blocking
try:  
	while True:
		line = q.get_nowait() # or q.get(timeout=.1)
		print(line)
except Empty:
	print('no output yet')
