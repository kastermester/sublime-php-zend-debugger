from .debugcontrols import pzd_socket_opened
from .debugcontrols import pzd_on_continue
from .phpserialize import Decoder
import sublime
import sublime_plugin

class PzdLocalsWindow(object):

    def __init__(self):
        global pzd_socket_opened, pzd_on_continue, pzd_paused_file

        self.socket = None
        self.opened = False
        self.view = None
        self.name = 'PZD: Locals'

        pzd_socket_opened += self.setup_socket
        pzd_on_continue += self.clear_locals

    def restore_view(self, view):
        if view.settings().get('pzd.locals_window', False):
            self.view = view
            self.opened = True
            self.set_text('')
            return

    def setup_socket(self, socket):
        if self.socket is not None:
            self.socket.server.session_ready -= self.fetch_locals
        self.socket = socket
        self.socket.server.session_ready += self.fetch_locals

    def fetch_locals(self, socket, msg):
        socket.get_stack_variables(self.process_locals)

    def process_locals(self, socket, message):
        if self.view is None:
            return

        def replace():
            self.set_text(self.format_locals(message['variable']))

        sublime.set_timeout(replace, 0)

    def format_locals(self, local):
        decoder = Decoder()
        deserialized = decoder.decode_value(local)
        return sublime.encode_value(deserialized, pretty=True)

    def set_text(self, text):
        self.view.set_read_only(False)
        self.view.run_command('pzd_set_text', {'text': text})
        self.view.run_command('goto_line', {'line': 1})
        self.view.set_read_only(True)

    def clear_locals(self):
        if self.view is not None:
            self.set_text('')

    def open(self):
        self.create_view()

    def close(self):
        self.destroy_view()

    def create_view(self):
        self.view = sublime.active_window().new_file()
        self.view.set_name(self.name)
        self.view.set_read_only(True)
        self.view.set_scratch(True)
        self.view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        settings = self.view.settings()
        settings.set('command_mode', False)
        settings.set('highlight_line', False)
        settings.set('gutters', False)
        settings.set('word_wrap', False)
        settings.set('always_show_minimap_viewport', False)
        settings.set('pzd.locals_window', True)
        self.opened = True

    def destroy_view(self, do_close=True):
        if do_close:
            sublime.active_window().focus_view(self.view)
            sublime.active_window().run_command('close')
        self.view = None
        self.opened = False


locals_window = PzdLocalsWindow()


class PzdToggleLocalsWindowCommand(sublime_plugin.WindowCommand):

    def run(self):
        global locals_window
        if not locals_window.opened:
            locals_window.open()
        else:
            locals_window.close()

    def description(self):
        return "Opens/Closes the PZD locals window"


class PzdLocalsWindowRestorer(sublime_plugin.EventListener):

    def on_load(self, view):
        global locals_window
        locals_window.restore_view(view)

    def on_close(self, view):
        global locals_window
        if view.settings().get('pzd.locals_window', False):
            locals_window.destroy_view(do_close=False)
