import sublime

def get_setting(key, default=None, view=None):
	try:
		if view is None:
			view = sublime.active_window().active_view()
		s = view.settings()

		if s.has("sublimepzd_%s" % key):
			return s.get("sublimepzd_%s" % s)
	except:
		pass
	return sublime.load_settings("SublimePZD.sublime-settings").get(key, default)

def local_to_server(filename, default=""):
	project_path_local = get_setting('project_path_local', None)
	project_path_server = get_setting('project_path_local', None)
	if project_path_local is not None and project_path_server is not None:
		return filename.replace(project_path_local, project_path_server)
	return filename

def server_to_local(filename, default=""):
	project_path_local = get_setting('project_path_local', None)
	project_path_server = get_setting('project_path_local', None)
	if project_path_local is not None and project_path_server is not None:
		return filename.replace(project_path_server, project_path_local)
	return filename
