from google.appengine.api import apiproxy_stub_map
from google.appengine.api import runtime
from utilities.logger import logThis, AEL_LEVEL_WARNING, AEL_LEVEL_INFO

import sys
sys.path.insert(0, 'libs')

def fashionista_register_shutdown_hook():
    apiproxy_stub_map.apiproxy.CancelApiCalls()
  
    # We can save state to datastore here or Log some statistics.
    logThis(AEL_LEVEL_WARNING, 'SHUTDOWN IN PROGRESS...')
    logThis(AEL_LEVEL_INFO,'CPU USAGE: %s' % runtime.cpu_usage())
    logThis(AEL_LEVEL_INFO,'MEMORY USAGE: %s' % runtime.memory_usage())
#Register a shutdown hook. Save state before being terminated.    
runtime.set_shutdown_hook(fashionista_register_shutdown_hook)