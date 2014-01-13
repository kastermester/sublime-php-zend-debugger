try:
	# Python 3
	from .php_zend_debugger import *
except (ValueError):
	from php_zend_debugger import *
