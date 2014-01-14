import sys
import imp

reload_mods = []
for mod in sys.modules:
    if mod.startswith('PHP Zend Debugger.php_zend_debugger.') and \
        sys.modules[mod] is not None and \
            mod != 'PHP Zend Debugger.php_zend_debugger.reloader':
        reload_mods.append(mod)


modules_order = ['PHP Zend Debugger.php_zend_debugger.' + x for x in [
    'phpserialize'
    'messagehandler',
    'path_mapper',
    'pyregionset'
    'event',
    'tcpserver',
    'debugger',
    'debugcontrols',
    'callstack'
    'localswindow'
]]

for mod in modules_order:
    if mod in reload_mods:
        m = sys.modules[mod]
        if 'on_module_reload' in m.__dict__:
            m.on_module_reload()
        imp.reload(sys.modules[mod])
