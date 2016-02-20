'''
Created on Dec 11, 2013
@author: primeuser=Hari
'''
import webapp2
import traceback
import pickle
import re
import sys
import datetime
from google.appengine.api import taskqueue
from utilities.logger import logThis, AEL_LEVEL_INFO, AEL_LEVEL_CRITICAL
from constants.constants import GAEQ_FOR_SUBTASK, SUBTASK_WEBREQ_PICKLED_TASKOBJ, dbG

class HandlerForMasterTaskQ(webapp2.RequestHandler):
    #HAS TO BE POST FOR QUEUE HANDLERS
    def post(self):
        try:
            logThis(AEL_LEVEL_INFO, 'START PROCESSING MASTERTASK FROM MasterTaskQ')
            #Do Something Here

            sys.path.insert(0, 'libs')

            dbG.populate('AppStore.GooglePlay_Master_DB')
            urls = dbG.toCrawl()

            intervals = [0, 10]
            for url in urls:
                self._addSubTaskToQueue(url) 
            logThis(AEL_LEVEL_INFO, 'MASTERTASK: Added SubTasks')
        #POST EXCEPT 
        except:
            logThis(AEL_LEVEL_CRITICAL, "EXP on HandlerForMasterTaskQ-" + traceback.format_exc())
    
    def _addSubTaskToQueue(self, taskObj):
        try:
            if taskObj != None:
                taskName = taskObj
                logThis(AEL_LEVEL_INFO, 'ADDING-SUBTASK [%s] TO SUB TASK Q '% taskName)
                
                task_name_on_Q = '[%s_%s]' % (taskName, 
                                              datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")) 
                task_name_on_Q = re.sub('[^a-zA-Z0-9_-]', '_', task_name_on_Q)
                
                taskqueue.add(queue_name=GAEQ_FOR_SUBTASK,name=task_name_on_Q,
                              params={'url': taskObj} )
                logThis(AEL_LEVEL_INFO, "NEW SUB TASK ON Q:" + task_name_on_Q)
                
        except taskqueue.TombstonedTaskError, e:
            logThis(AEL_LEVEL_CRITICAL, "EXCEPTION on _addSubTaskToQueue-" + traceback.format_exc())
        except taskqueue.DuplicateTaskNameError, e:
            logThis(AEL_LEVEL_CRITICAL, "EXCEPTION on _addSubTaskToQueue-" + traceback.format_exc())
        except:
            logThis(AEL_LEVEL_CRITICAL, "EXCEPTION on _addSubTaskToQueue-" + traceback.format_exc())
    
        
                
app = webapp2.WSGIApplication([('/_ah/queue/masterTaskQ', HandlerForMasterTaskQ)
                   ], debug=True)