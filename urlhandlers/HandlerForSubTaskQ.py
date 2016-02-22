'''
Created on Jan 10, 2014
@author: primeuser=Hari
'''
import webapp2
import traceback
import pickle
import datetime
import re
from utilities.logger import logThis, AEL_LEVEL_INFO, AEL_LEVEL_DEBUG,\
    AEL_LEVEL_CRITICAL
from constants.constants import SUBTASK_WEBREQ_PICKLED_TASKOBJ
from Tasks.AndroidCrawler import AndroidCrawler
from google.appengine.api import taskqueue
from constants.constants import *

class HandlerForSubTaskQ(webapp2.RequestHandler):
    def post(self):
        try:
            logThis(AEL_LEVEL_INFO, 'SUBTASK:START') 
            
            Queue = self.request.get('taskQ')

            if Queue == GAEQ_FOR_APPLE:
                print 'Apple Task'
                return

            ac = AndroidCrawler(self.request.get('url'))
            
            logThis(AEL_LEVEL_INFO, str(ac.isdone()) )

            # Retry if task didn't succeed
            if ac.isdone() == False and ac.retry() == True:
                taskName = self.request.get('url')
                
                print "THIS IS QUEUE", Queue
                task_name_on_Q = '[%s_%s]' % (taskName, 
                                              datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")) 
                task_name_on_Q = re.sub('[^a-zA-Z0-9_-]', '_', task_name_on_Q)

                taskqueue.add(queue_name=Queue,name=task_name_on_Q,
                              params={'url': self.request.get('url'), 'taskQ' : Queue} )
            elif ac.isdone() == True:
                print "TASK DONE"
                dbG.updateStatus([self.request.get('url')])

        #POST EXCEPT 
        except:
            logThis(AEL_LEVEL_CRITICAL, "EXP on HandlerForSubTaskQ-" + traceback.format_exc())
                        
app = webapp2.WSGIApplication([('/_ah/queue/googleTaskQ', HandlerForSubTaskQ)], debug=True)