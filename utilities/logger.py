'''
Created on Dec 1, 2013
@author: primeuser=Hari
'''
import logging
import os
from google.appengine.api import logservice
#Logging Specifics. HELPS to log to screen or to GAE logs.
logservice.AUTOFLUSH_ENABLED = True
logservice.AUTOFLUSH_EVERY_SECONDS = None
logservice.AUTOFLUSH_EVERY_BYTES = None
logservice.AUTOFLUSH_EVERY_LINES = 1 #CHANGE THIS TO 20 IF PROD

WE_APP_NAME = "GAETaskQueues-" 
ARE_WE_PYTH_APP = False
AEL_LEVEL_DEBUG = 0
AEL_LEVEL_INFO = 1
AEL_LEVEL_WARNING = 2
AEL_LEVEL_ERROR = 3
AEL_LEVEL_CRITICAL = 4
try:
    strEnv = os.environ['SERVER_SOFTWARE']
    if strEnv == None or strEnv == '':
        ARE_WE_PYTH_APP = True
    else:
        ARE_WE_PYTH_APP = False
except KeyError:
    ARE_WE_PYTH_APP = True

def logThis(nLogLevel, strMessage):
    if ARE_WE_PYTH_APP == True:
        print strMessage
        return
    if nLogLevel ==  AEL_LEVEL_DEBUG:
        logging.debug(WE_APP_NAME + strMessage)
        return
    if nLogLevel ==  AEL_LEVEL_INFO:
        logging.info(WE_APP_NAME + strMessage)
        return
    if nLogLevel ==  AEL_LEVEL_WARNING:
        logging.warning(WE_APP_NAME + strMessage)
        return
    if nLogLevel ==  AEL_LEVEL_ERROR:
        logging.error(WE_APP_NAME + strMessage)
        return
    if nLogLevel ==  AEL_LEVEL_CRITICAL:
        logging.critical(WE_APP_NAME + strMessage)
        return
    logservice.flush()
#End Logging specifics
if __name__=='__main__':
    logThis(0, "Helloooo")