import sys
import imp

reload_mods = []
for mod in sys.modules:
    if mod.startswith('php_zend_debugger') and sys.modules[mod] is not None:
        reload_mods.append(mod)

mods_load_order = [
    'php_zend_debugger.debug'
    'php_zend_debugger.callstackwindow'
    'php_zend_debugger.localswindow'
]

for mod in mods_load_order:
    if mod in reload_mods:
        m = sys.modules[mod]
        if 'on_module_reload' in m.__dict__:
            m.on_module_reload()
        imp.reload(sys.modules[mod])
