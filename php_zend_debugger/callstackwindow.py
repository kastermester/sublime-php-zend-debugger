from debug import pzd_socket_opened, pzd_on_continue
import sublime, sublime_plugin
from event import Event
import path_mapper

frame_depth = Event()

class PzdCallStackWindow(object):
	def __init__(self):
		global pzd_socket_opened, pzd_on_continue
		self.socket = None
		self.opened = False
		self.view = None
		self.name = 'PZD: Callstack'

		pzd_socket_opened += self.setup_socket
		pzd_on_continue += self.clear_callstack

	def restore_view(self, view):
		if view.settings().get('pzd.callstack_window', False):
			self.view = view
			self.opened = True
			self.set_text('')
			return

	def setup_socket(self, socket):
		if self.socket is not None:
			self.unbind_socket(socket)
		self.socket = socket
		self.bind_socket(socket)

	def unbind_socket(self, socket):
		self.socket.server.session_ready -= self.fetch_callstack

	def bind_socket(self, socket):
		self.socket.server.session_ready += self.fetch_callstack

	def fetch_callstack(self, socket, message):
		self.socket.get_callstack(self.process_callstack)

	def process_callstack(self, socket, message):
		if self.view is None:
			return
		def replace():
			global frame_depth
			self.set_text(self.format_callstack(message['callstack']))
			self.view.add_regions("pzd.callstack_frame", [self.view.line(0)], "stackframe", '', sublime.DRAW_EMPTY_AS_OVERWRITE)
			frame_depth(0)

		sublime.set_timeout(replace, 0)

	def format_callstack(self, callstack):
		n = len(callstack)

		result = []

		while len(callstack) > 0:
			frame = callstack.pop()
			if len(frame['called_filename']) > 0:
				result.append('%s:%d' % (path_mapper.server_to_local(frame['called_filename']), frame['called_lineno']))
		return '\n'.join(result)

	def set_text(self, text):
		self.view.set_read_only(False)
		edit = self.view.begin_edit()
		self.view.replace(edit, sublime.Region(0, self.view.size()), text)
		self.view.sel().clear()
		self.view.run_command('goto_line', { 'line': 0})
		self.view.end_edit(edit)
		self.view.set_read_only(True)

	def clear_callstack(self):
		if self.view is not None:
			self.set_text('')
			self.view.erase_regions('pzd.callstack_frame')


	def open(self):
		self.create_view()

	def close(self):
		self.destroy_view()

	def create_view(self):
		self.view = sublime.active_window().new_file()
		self.view.set_name(self.name)
		self.view.set_read_only(True)
		self.view.set_scratch(True)
		settings = self.view.settings()
		settings.set('command_mode', False)
		settings.set('highlight_line', False)
		settings.set('gutters', False)
		settings.set('word_wrap', False)
		settings.set('always_show_minimap_viewport', False)
		settings.set('pzd.callstack_window', True)
		self.opened = True

	def destroy_view(self, do_close = True):
		if do_close:
			sublime.active_window().focus_view(self.view)
			sublime.active_window().run_command('close')
		self.view = None
		self.opened = False


callstack_window = PzdCallStackWindow()


class PzdToggleCallstackWindowCommand(sublime_plugin.WindowCommand):
	def run(self):
		global callstack_window
		if not callstack_window.opened:
			callstack_window.open()
		else:
			callstack_window.close()

	def description(self):
		return "Opens/Closes the PZD callstack window"

class PzdCallstackWindowRestorer(sublime_plugin.EventListener):
	def on_load(self, view):
		global callstack_window
		callstack_window.restore_view(view)
	def on_close(self, view):
		global callstack_window
		if view.settings().get('pzd.callstack_window', False):
			callstack_window.destroy_view(do_close=False)

class PzdOpenCallstackFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global callstack_window, frame_depth
		sel = self.view.sel()
		first = True
		for r in sel:
			for line in self.view.split_by_newlines(r):
				line = self.view.line(line)
				row,col = self.view.rowcol(line.begin())

				filename = self.view.substr(line)
				sublime.active_window().focus_group(0)
				view = sublime.active_window().open_file(filename, sublime.TRANSIENT | sublime.ENCODED_POSITION)
				if first:
					frame_depth(row)
					self.view.add_regions("pzd.callstack_frame", [line], "stackframe", '', sublime.DRAW_EMPTY_AS_OVERWRITE)

				first = False

	def description(self):
		return "Opens the callstack file selected"

	def is_enabled(self):
		return self.view.settings().get('pzd.callstack_window', False) and self.view.size() > 0
