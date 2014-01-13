import imp
import sys

if 'php_zend_debugger.reloader' in sys.modules:
    imp.reload(sys.modules['php_zend_debugger.reloader'])
import php_zend_debugger.reloader
