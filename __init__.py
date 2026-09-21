#import imp
from . import __version__ as version
try:
	__version__ 	= version.version
except:
	__version__ 	= version
__email__		= "licface@yahoo.com"
__author__		= "licface@yahoo.com"

from .debug import *
