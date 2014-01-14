from imp import reload
import sys
import sublime

st_version = 2

if int(sublime.version()) > 3000:
    st_version = 3

reloader_name = 'php_zend_debugger.reloader'

if st_version == 3:
    reloader_name = 'PHP Zend Debugger.' + reloader_name

if reloader_name in sys.modules:
    reload(sys.modules[reloader_name])

if 'php_zend_debugger.reloader' in sys.modules:
    imp.reload(sys.modules['php_zend_debugger.reloader'])

#try:
    # Python 3
from .php_zend_debugger import reloader
#from .php_zend_debugger import debugcontrols
#from .php_zend_debugger import callstackwindow
#from .php_zend_debugger import localswindow

from .php_zend_debugger.debugcontrols import PzdDebugCommand
from .php_zend_debugger.debugcontrols import PzdStopDebugCommand
from .php_zend_debugger.debugcontrols import PzdToggleBreakpointCommand
from .php_zend_debugger.debugcontrols import PzdRestoreBreakpointInformation
from .php_zend_debugger.debugcontrols import PzdStepOverCommand
from .php_zend_debugger.debugcontrols import PzdStepIntoCommand
from .php_zend_debugger.debugcontrols import PzdStepOutCommand
from .php_zend_debugger.debugcontrols import PzdContinueCommand
from .php_zend_debugger.debugcontrols import PzdDoNotOpenWindowsInMyGroupsPlzListener
from .php_zend_debugger.callstackwindow import PzdCallStackWindow
from .php_zend_debugger.callstackwindow import PzdToggleCallstackWindowCommand
from .php_zend_debugger.callstackwindow import PzdCallstackWindowRestorer
from .php_zend_debugger.callstackwindow import PzdOpenCallstackFileCommand
from .php_zend_debugger.callstackwindow import PzdSetTextCommand
from .php_zend_debugger.localswindow import PzdLocalsWindow
from .php_zend_debugger.localswindow import PzdToggleLocalsWindowCommand
from .php_zend_debugger.localswindow import PzdLocalsWindowRestorer


def plugin_loaded():
    from .php_zend_debugger.localswindow import locals_window
    from .php_zend_debugger.callstackwindow import callstack_window
    for window in sublime.windows():
        for view in window.views():
            callstack_window.restore_view(view)
            locals_window.restore_view(view)
            PzdRestoreBreakpointInformation.load_breakpoints_for_view(None, view)
