import threading, asyncore, signal
from tcpserver import TcpServer
from messagehandler import MessageHandler
from event import Event

class DebuggerServer(threading.Thread):
	def __init__(self, host, port):
		threading.Thread.__init__(self, target=self.run)
		self.session_started = Event()
		self.session_ready = Event()
		self.process_file = Event()
		self.header_output = Event()
		self.php_error = Event()
		self.output = Event()
		self.script_end = Event()
		self.host = host
		self.port = port

	def start(self):
		self.previous_sigint_listener = signal.signal(signal.SIGINT, self.handle_sigint)
		threading.Thread.start(self)

	def run(self):
		self.listener = TcpServer(self.host, self.port, self.socket_opened)
		asyncore.loop()

	def handle_sigint(self, signum, frame):
		previous = self.previous_sigint_listener
		self.stop_debug()
		if previous is not None:
			previous()

	def stop_debug(self):
		if self.listener is not None:
			signal.signal(signal.SIGINT, self.previous_sigint_listener)
			self.previous_sigint_listener = None
			self.listener.close()
			self.listener = None

	def socket_opened(self, socket):
		DebuggerSession(socket, self)

class DebuggerSession:
	def __init__(self, socket, server):
		self.socket = socket
		self.socket.set_read_callback(self.msg_received)
		self.response_callbacks = {}
		self.msg_callbacks = {}
		self.server = server
		self.req_id = -128
		self.breakpoints = {}

		self.subscribe_to('MSG_SESS_START', self.session_started)
		self.subscribe_to('MSG_READY', server.session_ready)
		self.subscribe_to('MSG_START_PROCESS_FILE', server.process_file)
		self.subscribe_to('MSG_HEADER_OUTPUT', server.header_output)
		self.subscribe_to('MSG_OUTPUT', server.output)
		self.subscribe_to('MSG_PHP_ERROR', server.php_error)
		self.subscribe_to('MSG_SCRIPT_END', self.script_end)

	def msg_received(self, msg):
		msg = MessageHandler.read_message(msg)
		if 'req_id' in msg:
			req_id = msg['req_id']
			response_callback = self.response_callbacks.pop(req_id, None)
			if response_callback is not None:
				response_callback(self, msg)
				return

		id = msg['id']
		if not id in self.msg_callbacks:
			raise Exception("%s not registered as a callback" % id)
		return self.msg_callbacks[id](self, msg)

	def send(self, msg, callback=None):
		msg['req_id'] = self.req_id
		self.req_id += 1
		if self.req_id == 128:
			self.req_id = -128
		if callback is not None:
			self.response_callbacks[msg['req_id']] = callback
		self.socket.write(MessageHandler.encode_message(msg))

	def subscribe_to(self, id, callback):
		if id in self.msg_callbacks:
			raise Exception("%s already in message callbacks" % id)
		self.msg_callbacks[id] = callback

	@staticmethod
	def session_started(self, msg):
		self.version = 2006040705
		self.send({'id': 'MSG_SET_PROTOCOL', 'protocol_id': 2006040705}, self.protocol_set)
		self.server.session_started(self, msg)

	@staticmethod
	def script_end(self, msg):
		self.send({'id': 'MSG_SESS_CLOSE'})
		self.server.script_end(self, msg)

	@staticmethod
	def protocol_set(self, msg):
		if msg['protocol_id'] != self.version:
			raise Exception("Protocol does not match %d" % msg['protocol_id'])
		msg = {'id': 'MSG_START'}
		self.send(msg, self.start_reply)

	@staticmethod
	def start_reply(self, msg):
		if msg['status'] == -1:
			raise Exception("Unexpected status %d" % msg['status'])

	def continue_process(self):
		msg = {'id': 'MSG_CONTINUE_PROCESS_FILE'}
		self.send(msg)

	def close(self):
		self.socket.close()

	def stop_debug(self):
		self.server.stop_debug()

	def set_breakpoint(self, file, line):
		def breakpoint_set(self, msg):
			if msg['status'] != 0:
				raise Exception("Could not set breakpoint")
			print file + ':' + str(line)
			self.breakpoints[file + ':' + str(line)] = msg['breakpoint_id']

		breakpoint = {
			'id': 'MSG_ADD_BREAKPOINT',
			'file': file,
			'lineno': line,
			'type': 1,
			'lifetime': 2
		}
		self.send(breakpoint, breakpoint_set)
	def remove_breakpoint(self, file, line):
		key = file + ':' + str(line)
		if not key in self.breakpoints:
			raise Exception("Breakpoint %s not found" % key)
		bp = self.breakpoints[key]
		rm = {
			'id': 'MSG_DEL_BREAKPOINT',
			'bp_id': bp
		}
		def breakpoint_removed(self, msg):
			if msg['status'] != 0:
				raise Exception("Could not remove breakpoint")
			self.breakpoints.pop(key)
		self.send(rm, self.breakpoint_removed)


	def step_over(self):
		msg = {
			'id': 'MSG_STEP_OVER'
		}
		self.send(msg, self.step_over_completed)

	@staticmethod
	def step_over_completed(self, msg):
		if msg['status'] != 0:
			raise Exception("Could not step over")

	def step_out(self):
		msg = {
			'id': 'MSG_STEP_OUT'
		}
		self.send(msg, self.step_out_completed)

	@staticmethod
	def step_out_completed(self, msg):
		if msg['status'] != 0:
			raise Exception("Could not step out")

	def step_into(self):
		msg = {
			'id': 'MSG_STEP_INTO'
		}
		self.send(msg, self.step_into_completed)

	@staticmethod
	def step_into_completed(self, msg):
		if msg['status'] != 0:
			raise Exception("Could not step into")

	def debug_continue(self):
		msg = {
			'id': 'MSG_GO'
		}
		self.send(msg, self.continue_completed)

	def get_callstack(self, callback):
		msg = {
			'id': 'MSG_GET_CALL_STACK'
		}
		self.send(msg, callback)

	@staticmethod
	def continue_completed(self, msg):
		if msg['status'] != 0:
			raise Exception("Could not step over")

	def get_stack_variables(self, depth, callback):
		msg  = {
			'id': 'MSG_GET_STACK_VAR',
			'stack_depth': depth,
			'depth': 1,
			'var_name': '',
			'path': []
		}
		self.send(msg, callback)
