import sublime
import re
import os


def get_setting(key, default=None, view=None):
    try:
        if view is None:
            view = sublime.active_window().active_view()
        s = view.settings()
        if s.has("sublimepzd_%s" % key):
            return expand_path(s.get("sublimepzd_%s" % key), view.window())
    except:
        pass
    s = sublime.load_settings("SublimePZD.sublime-settings")
    value = s.get(key, default)
    if value is not None:
        return expand_path(value, view.window())
    else:
        return None


def local_to_server(filename, view=None,):
    project_path_local = get_setting('project_path_local', view=view)
    project_path_server = get_setting('project_path_server', view=view)
    if project_path_local is not None and project_path_server is not None:
        return filename.replace(project_path_local, project_path_server)
    return filename


def server_to_local(filename, view=None):
    project_path_local = get_setting('project_path_local', view=view)
    print project_path_local
    project_path_server = get_setting('project_path_server', view=view)
    print project_path_server
    if project_path_local is not None and project_path_server is not None:
        return filename.replace(project_path_server, project_path_local)
    return filename


def expand_path(value, window):
    if window is None:
        # Views can apparently be window less, in most instances getting
        # the active_window will be the right choice (for example when
        # previewing a file), but the one instance this is incorrect
        # is during Sublime Text 2 session restore. Apparently it's
        # possible for views to be windowless then too and since it's
        # possible that multiple windows are to be restored, the
        # "wrong" one for this view might be the active one and thus
        # ${project_path} will not be expanded correctly.
        #
        # This will have to remain a known documented issue unless
        # someone can think of something that should be done plugin
        # side to fix this.
        window = sublime.active_window()

    get_existing_files = \
        lambda m: \
        [
            path
            for f in window.folders()
            for path in [os.path.join(f, m.group('file'))]
            if os.path.exists(path)
        ]

    value = re.sub(
        r'\${project_path:(?P<file>[^}]+)}',
        lambda m: len(
            get_existing_files(m)
        ) > 0 and get_existing_files(m)[0] or m.group('file'), value
    )
    value = re.sub(
        r'\${env:(?P<variable>.*)}',
        lambda m: os.getenv(m.group('variable')), value
    )
    if os.getenv("HOME"):
        value = re.sub(r'\${home}', re.escape(os.getenv('HOME')), value)
    value = re.sub(
        r'\${folder:(?P<file>.*)}',
        lambda m: os.path.dirname(m.group('file')), value
    )
    value = value.replace('\\', os.sep)
    value = value.replace('/', os.sep)

    return value
