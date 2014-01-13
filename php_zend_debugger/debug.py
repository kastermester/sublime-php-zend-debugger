import sublime, sublime_plugin
from debugger import DebuggerServer
from pyregionset import PyRegionSet
from event import Event
import path_mapper

active_debugger = None
pzd_breakpoints = {}
pzd_socket = None
pzd_paused_file = None

pzd_socket_opened = Event()
pzd_on_continue = Event()

class PzdDebugCommand(sublime_plugin.WindowCommand):
	def run(self):
		global active_debugger
		if active_debugger is not None:
			active_debugger.stop_debug()
		debugger = DebuggerServer('0.0.0.0', 10137)
		active_debugger = debugger
		debugger.start()
		print("Debugger started")
		debugger.session_started += self.session_started
		debugger.process_file += self.process_file
		debugger.session_ready += self.session_paused
		debugger.script_end += self.script_end

	def process_file(self, socket, msg):
		def process():
			global pzd_breakpoints
			filename = path_mapper.server_to_local(msg['filename'])
			for bp in pzd_breakpoints.get(filename, []):
				socket.set_breakpoint(msg['filename'], bp)
			socket.continue_process()
		sublime.set_timeout(process, 0)

	def is_enabled(self):
		global active_debugger
		return active_debugger is None

	def script_end(self, socket, msg):
		global pzd_socket, pzd_paused_file
		pzd_socket = None
		pzd_paused_file = None
		socket.close()

	def session_started(self, socket, msg):
		global pzd_socket, pzd_socket_opened
		pzd_socket = socket
		pzd_socket_opened(socket)

	def session_paused(self, socket, msg):
		def process():
			global pzd_paused_file
			filename = path_mapper.server_to_local(msg['filename'])
			line = msg['lineno']
			def open_file():
				global pzd_paused_file
				view = sublime.active_window().open_file('%s:%d' % (filename, line), sublime.ENCODED_POSITION)
				pzd_paused_file = view
				self.highlight_line(view, line)
			sublime.set_timeout(open_file, 0)
		sublime.set_timeout(process, 0)

	def highlight_line(self, view, line):
		view.run_command('goto_line', {"line": line})
		r = view.sel()[0]
		r = view.line(r)
		# If you open a new file, and then try to add the region right away, it won't work
		def add_current_marker():
			view.add_regions("pzd.active_line", [r], "support.class.string.php", '', sublime.DRAW_OUTLINED)

			test = view.get_regions('pzd.active_line')
			if len(test) == 0:
				sublime.set_timeout(add_current_marker, 100)

		add_current_marker()


class PzdStopDebugCommand(sublime_plugin.WindowCommand):
	def run(self):
		global active_debugger
		if active_debugger is not None:
			active_debugger.stop_debug()
			active_debugger = None
			print("Debugger stopped")

	def is_enabled(self):
		global active_debugger
		return active_debugger is not None


class PzdToggleBreakpointCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global pzd_breakpoints, pzd_socket
		regions_to_toggle = PyRegionSet([pzd_normalize_region(self.view, r) for r in self.view.sel()])
		existing_regions = PyRegionSet(self.view.get_regions("pzd.breakpoint"))
		filename = path_mapper.local_to_server(self.view.file_name())
		if pzd_socket is not None:
			for r in regions_to_toggle:
				if not existing_regions.contains(r):
					pzd_socket.set_breakpoint(filename, pzd_region_to_line(self.view, r))

		for r in existing_regions:
			r = pzd_normalize_region(self.view, r)
			if regions_to_toggle.contains(r):
				regions_to_toggle.subtract(r)
				if pzd_socket is not None:
					pzd_socket.remove_breakpoint(filename, pzd_region_to_line(self.view, r))
			else:
				regions_to_toggle.add(r)
		self.view.add_regions("pzd.breakpoint", regions_to_toggle, "support.function.string.php", 'circle', sublime.PERSISTENT)

		points = []
		for r in regions_to_toggle:
			points.append(pzd_region_to_line(self.view, r))

		if len(points) == 0:
			pzd_breakpoints.pop(self.view.file_name(), None)
		else:
			pzd_breakpoints[self.view.file_name()] = points

	def is_enabled(self):
		return sublime.active_window().active_view().file_name() is not None

class PzdRestoreBreakpointInformation(sublime_plugin.EventListener):
	def load_breakpoints_for_view(self, view):
		global pzd_breakpoints, pzd_socket


		breakpoints = view.get_regions("pzd.breakpoint")
		lines = []
		filename = view.file_name()
		if filename is None:
			return
		server_filename = path_mapper.local_to_server(filename)
		for r in breakpoints:
			r = pzd_normalize_region(view, r)
			line = pzd_region_to_line(view, r)
			lines.append(line)
			if pzd_socket is not None:
				pzd_socket.set_breakpoint(server_filename, line)

		if len(lines) == 0:
			pzd_breakpoints.pop(filename, None)
		else:
			pzd_breakpoints[filename] = lines

	def on_load(self, view):
		self.load_breakpoints_for_view(view)

	def on_post_save(self, view):
		global pzd_breakpoints, pzd_socket
		filename = view.file_name()
		server_filename = path_mapper.local_to_server(filename)

		if not filename in pzd_breakpoints:
			return

		bp_lines = frozenset(pzd_breakpoints[filename])

		if pzd_socket is not None:
			for bp in bp_lines:
				pzd_socket.remove_breakpoint(server_filename, bp)
		existing_lines = []

		regions = view.get_regions('pzd.breakpoint')
		for region in regions:
			for line in view.lines(region):
				existing_lines.append(pzd_region_to_line(line))

		existing_lines = frozenset(existing_lines)
		pzd_breakpoints[filename] = existing_lines

		if pzd_socket is not None:
			for line in existing_lines:
				pzd_socket.set_breakpoint(server_filename, line)


class PzdStepOverCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global pzd_socket, pzd_paused_file
		pzd_socket.step_over()
		pzd_paused_file.erase_regions('pzd.active_line')
		pzd_on_continue()
		pzd_paused_file = None

	def is_enabled(self):
		global pzd_socket, pzd_paused_file
		return pzd_socket is not None and pzd_paused_file is not None

	def description(self):
		return "Steps over the current line in the PHP debugging session"

class PzdStepIntoCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global pzd_socket, pzd_paused_file
		pzd_socket.step_into()
		pzd_paused_file.erase_regions('pzd.active_line')
		pzd_on_continue()
		pzd_paused_file = None

	def is_enabled(self):
		global pzd_socket, pzd_paused_file
		return pzd_socket is not None and pzd_paused_file is not None


	def description(self):
		return "Steps into the current function call in the debugging session"

class PzdStepOutCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global pzd_socket, pzd_paused_file
		pzd_socket.step_out()
		pzd_paused_file.erase_regions('pzd.active_line')
		pzd_on_continue()
		pzd_paused_file = None

	def is_enabled(self):
		global pzd_socket, pzd_paused_file
		return pzd_socket is not None and pzd_paused_file is not None


	def description(self):
		return "Steps out of the current function call in the debugging session"

class PzdContinueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global pzd_socket, pzd_paused_file, pzd_on_continue
		pzd_socket.debug_continue()
		pzd_paused_file.erase_regions('pzd.active_line')
		pzd_on_continue()
		pzd_paused_file = None

	def is_enabled(self):
		global pzd_socket, pzd_paused_file
		return pzd_socket is not None and pzd_paused_file is not None

	def description(self):
		return "Continues execution of the PHP script"


def pzd_normalize_region(view, region):
	row, col = view.rowcol(view.line(region).begin())
	textpoint = view.text_point(row, col)
	return sublime.Region(textpoint, textpoint)
def pzd_region_to_line(view, region):
	row, col = view.rowcol(region.begin())
	return row + 1

bpLoader = PzdRestoreBreakpointInformation()
for window in sublime.windows():
	for view in window.views():
		bpLoader.on_load(view)
