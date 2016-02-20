'''
Created on Nov 25, 2013
@author: primeuser=Hari
'''  
import traceback
import datetime
from google.appengine.api import taskqueue
import re
import webapp2
from utilities.logger import logThis, AEL_LEVEL_INFO, AEL_LEVEL_CRITICAL
from constants.constants import GAET_MASTERTASK_NAME, GAEQ_FOR_MASTERTASK

class QueueAMasterTask(webapp2.RequestHandler): 
    def get(self):
        try:
            dt =datetime.datetime.now()
            logThis(AEL_LEVEL_INFO, 'Master Task added to its Q at[%s]' %(dt))            
            task_name = GAET_MASTERTASK_NAME + str(datetime.datetime.now())
            task_name = re.sub('[^a-zA-Z0-9_-]', '_', task_name)
            taskqueue.add(queue_name=GAEQ_FOR_MASTERTASK,name=task_name)
            logThis(AEL_LEVEL_INFO, "OK-MASTER TASK ADD")
        except taskqueue.DuplicateTaskNameError:
            logThis(AEL_LEVEL_CRITICAL, "EXCEPTION on QueueAMasterTask-" + traceback.format_exc())
        except:
            logThis(AEL_LEVEL_CRITICAL, "EXP on QueueAMasterTask-" + traceback.format_exc())
            
app = webapp2.WSGIApplication([('/QueueAMasterTask', QueueAMasterTask)
                   ], debug=True)